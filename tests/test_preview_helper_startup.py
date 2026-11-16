import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
p=module('helper_p','prepare-preview-helper-startup.py')
a=module('helper_a','analyze-preview-helper-startup.py')


def source(variant):
    # Synthetic preparation control flow: no retained evidence or installed packages.
    resolution='binds = verifyRuntime(runtime);' if variant=='A' else 'if (held) { binds = GenerationAccess::binds(held); } else { binds = verifyRuntime(runtime); }'
    broad='    StandbyTrace::event("helper_prepare", "begin", &process);' if variant=='A' else '  StandbyTrace::Scope trace("helper_prepare", this, -1);'
    text=broad+'''
    QStringList binds;
    try {
      RESOLUTION
    } catch (...) { throw; }
    CANCEL {
      throw Failure{};
    }
    for (const auto* tool : {"/usr/bin/bwrap", "/usr/bin/systemd-run", "/usr/bin/systemctl"}) {
      if (!QFileInfo(tool).isExecutable()) { throw Failure{}; }
    }
    unit = "holonight-images-" + QUuid::createUuid().toString(QUuid::Id128) + ".scope";
    process.setProcessEnvironment(environment());
    process.start("/usr/bin/systemd-run", command);
    if (!process.waitForStarted(1000)) {
      throw Failure{};
    }
    launched = true;
    while (group.isEmpty()) {
      CHECK
      group = groupOf(process.processId(), unit);
    }
    LIMIT_CHECK
    if (fileBytes(group + "/memory.max").trimmed() != QByteArray::number(scopeMemoryCeiling) ||
        fileBytes(group + "/memory.swap.max").trimmed() != QByteArray::number(scopeSwapCeiling)) { throw Failure{}; }
RECEIVE
    if (process.write("G", 1) != 1) { throw Failure{}; }
    process.waitForBytesWritten(5);
    try {
      if (receive(1) != "R") { throw ProtocolError{}; }
    } catch (...) { throw; }
SESSION
FINAL
'''
    text=text.replace('RESOLUTION',resolution).replace('CANCEL','if (cancelled.load())' if variant=='A' else 'if (cancelled->load())')
    text=text.replace('CHECK','check();' if variant=='A' else 'check(false);',1)
    text=text.replace('LIMIT_CHECK','check();  // Own the scope before cancellation; keep the trusted input gate closed.' if variant=='A' else 'check();')
    text=text.replace('RECEIVE','    auto receive = [&](qint64 size) { return QByteArray{}; };' if variant=='A' else '')
    text=text.replace('SESSION','''    if (session) {
      const auto length = qFromBigEndian<quint32>(receive(4).constData());
      if (length == 0 || length > controlCeiling) { throw ProtocolError{}; }
      const auto ready = parseControl(receive(length));
      integer(ready, "sessionVersion", 1, 1);
      if (ready.size() != 2 || ready["command"] != "ready") { throw ProtocolError{}; }
    }''' if variant=='C' else '')
    return text.replace('FINAL','''    StandbyTrace::event("helper_ready", "point", &process);
    StandbyTrace::event("helper_prepare", "end", &process);
    result.startup = elapsed.elapsed();''' if variant=='A' else '''    result.startup = elapsed.elapsed();
    result.status = RuntimeStatus::Success;
    StandbyTrace::event("helper_ready", "point", this);
    prepared = true;''')


def event(span,ns,edge,operation='preparation',parent=None,**kw):
    return dict(version=1,ns=ns,pid=10,tid=11,span=span,parent=parent,operation=operation,edge=edge,
                outcome='unavailable' if edge=='begin' else 'returned',invocation='i',host='host',boot='boot',
                clock='CLOCK_MONOTONIC',service=2,observation=1,job=3,worker=4,preparation=None,
                request_generation=5,runtime_generation=None,**kw)
def trace(events): return '\n'.join('HELPER_STARTUP '+json.dumps(e) for e in events)
CONTEXT=dict(invocation='i',block=0,arm='instrumented',warmup=False,fixture='3200x2400.png')


class HelperTests(unittest.TestCase):
    def setUp(self):
        self.no_process=patch('subprocess.Popen',side_effect=AssertionError('process execution disabled'))
        self.no_process.start(); self.addCleanup(self.no_process.stop)

    def account(self,events,**kw):
        # Lifecycle validation has its own retained fixture suite; these synthetic
        # streams exercise the supplemental contract independently.
        with patch.object(a.d,'analyze',return_value=dict(assessment_available=True)):
            return a.account(trace(events),'synthetic.stderr','C',[{}]*5,CONTEXT,**kw)

    def test_missing_duplicate_anchors_fail(self):
        for variant in ('A','C'):
            text=source(variant)
            for bad in (text.replace('process.start("/usr/bin/systemd-run", command);',''),
                        text+'\n    process.start("/usr/bin/systemd-run", command);'):
                with self.assertRaisesRegex(ValueError,'missing/duplicate'): p.instrument(bad,variant)

    def test_exact_reverse_and_readiness_differences(self):
        for variant in ('A','C'):
            text=source(variant); new,edits=p.instrument(text,variant)
            self.assertEqual(p.reconstruct(new,edits),text)
            self.assertEqual('session_readiness_payload_receive' in new,variant=='C')
            self.assertLess(new.index('helper_discovery.finish()'),new.index('memory.max'))
            self.assertLess(new.index('memory.swap.max'),new.index('process.write("G"'))
            self.assertIn('check(false)' if variant=='C' else 'check();',new)
            self.assertIn('receive(1) != "R"',new)

    def test_frozen_schedule_populations(self):
        protocol=p.protocol(); rows=protocol['schedule']
        self.assertEqual(len(rows),36); self.assertEqual(sum(r['observations'] for r in rows if not r['warmup']),150)
        self.assertEqual(sum(r['warmup'] for r in rows),6)
        for block in range(5):
            order=p.COMBINATIONS[block:]+p.COMBINATIONS[:block]
            if block%2: order=list(reversed(order))
            self.assertEqual([(r['variant'],r['arm']) for r in rows if r['block']==block],order)
        self.assertEqual((protocol['timeout_seconds'],protocol['termination_grace_seconds'],protocol['retries']),(30,5,0))

    def test_nested_overlap_union_and_parent_exclusive(self):
        events=[event(1,0,'begin'),event(2,10,'begin','session_readiness',1),
                event(3,20,'begin','session_readiness_length',2),event(3,40,'end','session_readiness_length',2),
                event(2,60,'end','session_readiness',1),event(1,100,'end')]
        result=self.account(events)
        self.assertEqual(result['status'],'complete')
        self.assertEqual(result['spans'][0]['exclusive_ns'],50)
        self.assertEqual(result['spans'][1]['exclusive_ns'],30)
        self.assertEqual(result['windows'][0]['covered_ns'],50)
        self.assertEqual(a.union([(10,40),(20,60)]),[[10,60]])
        self.assertEqual(result['records'][0]['raw']['line'],1)

    def test_identity_mismatch_and_duplicate_boundaries_block(self):
        for field,value in [('worker',99),('request_generation',99),('invocation','other'),('tid',12)]:
            end=event(1,100,'end'); end[field]=value
            self.assertEqual(self.account([event(1,0,'begin'),end])['status'],'blocked')
        self.assertEqual(self.account([event(1,0,'begin')]*2+[event(1,100,'end')])['status'],'blocked')

    def test_exception_and_missing_boundaries(self):
        end=event(1,100,'end');end['outcome']='exception'
        result=self.account([event(1,0,'begin'),event(2,10,'begin','launcher_checks',1),end])
        self.assertEqual(result['spans'][0]['end']['outcome'],'exception')
        self.assertIsNone(result['spans'][0]['exclusive_ns'])
        self.assertTrue(result['unavailable'])

    def test_cyclic_parent_and_malformed_boundaries_block(self):
        self.assertEqual(self.account([event(1,0,'begin',parent=1),event(1,100,'end',parent=1)])['status'],'blocked')
        bad=event(1,0,'begin'); bad['ns']=True
        self.assertTrue(a.parse(trace([bad]),'synthetic')[1])
        bad=event(1,0,'begin'); bad['request_generation']=0
        self.assertTrue(a.parse(trace([bad]),'synthetic')[1])

    def test_analyzer_failure_is_sealed(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); out=root/'out'
            result=a.run(root/'missing',root/'samples',root/'context','C',out)
            self.assertEqual(result['status'],'blocked');p.o.check_output(out)

    def test_source_citations_follow_operations(self):
        citation=dict(file='frozen.cpp',line=7,sha256='hash',text='HelperStartupTrace::Scope root("preparation");')
        result=self.account([event(1,0,'begin'),event(1,100,'end')],source_citations=[citation])
        self.assertEqual(result['source_availability'],'bound')
        self.assertEqual(result['spans'][0]['source_citations'],[citation])

    def test_populations_stay_separate(self):
        for field,value in [('fixture','other.png'),('block',7),('arm','validation')]:
            context=dict(CONTEXT,**{field:value})
            with self.assertRaises(ValueError): a.account('','source','C',[{}]*5,context)
        result=self.account([event(1,0,'begin'),event(1,100,'end')])
        self.assertEqual(result['population'],CONTEXT)
        self.assertIsNone(result['records'][0]['runtime_generation'])
        self.assertEqual(result['records'][0]['request_generation'],5)

    def test_scheduler_requires_clock_lifetime_and_no_loss(self):
        events=[event(1,10,'begin'),event(1,90,'end')]
        capture=dict(version=2,clock=dict(name='CLOCK_MONOTONIC',provenance=dict(host='host',boot_id='boot')),
                     start_ns=0,stop_ns=100,export_complete=True,events=[],
                     tasks=[dict(key=[10,11,1],start_ns=0,stop_ns=100,initial='running',cpu=0,
                                 identity_evidence=[dict(invocation='i',pid=10,tid=11,ns=n) for n in (10,90)])])
        self.assertTrue(self.account(events,capture=capture)['spans'][0]['scheduler']['available'])
        for change in ('clock','host','boot','loss','lifetime','identity'):
            bad=copy.deepcopy(capture)
            if change=='clock': bad['clock']['name']='realtime'
            if change=='host': bad['clock']['provenance']['host']='other'
            if change=='boot': bad['clock']['provenance']['boot_id']='other'
            if change=='loss': bad['events']=[dict(kind='loss',ns=50,count=1)]
            if change=='lifetime': bad['tasks'][0]['stop_ns']=50
            if change=='identity': bad['tasks'][0]['identity_evidence']=[]
            self.assertFalse(self.account(events,capture=bad)['spans'][0]['scheduler']['available'],change)

    def test_failed_preparation_is_sealed_and_collision_preserved(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence=root/'evidence'; evidence.mkdir(); out=root/'out'
            result=p.prepare(evidence,root/'missing.json',out)
            self.assertEqual(result['status'],'blocked');p.o.check_output(out)
            before=p.o.inventory(out)
            with self.assertRaises(ValueError):p.prepare(evidence,root/'missing.json',out)
            self.assertEqual(p.o.inventory(out),before)

    def test_destination_cannot_modify_recorded_input_package(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence=root/'evidence'; evidence.mkdir()
            source_root=root/'prepared';source_root.mkdir()
            source_file=source_root/'source.cpp';source_file.write_text('unchanged')
            p.write(evidence/'integrity.json',dict(consumed={str(source_file):p.o.digest(source_file)}))
            out=source_root/'new-output'
            with self.assertRaisesRegex(ValueError,'disjoint'):
                p.prepare(evidence,root/'missing.json',out)
            self.assertFalse(out.exists());self.assertEqual(source_file.read_text(),'unchanged')

    def test_verification_must_bind_exact_assessment_seal(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence=root/'evidence';evidence.mkdir()
            p.write(evidence/'assessment.json',dict(status='complete'));p.o.seal(evidence)
            verification=root/'verification.json'
            p.write(verification,dict(status='passed',assessment_seal='wrong'))
            result=p.prepare(evidence,verification,root/'out')
            self.assertEqual(result['status'],'blocked')
            self.assertIn('verification binding mismatch',result['failure']);p.o.check_output(root/'out')

    def test_input_drift_blocks_and_seals(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence=root/'evidence';evidence.mkdir();out=root/'out'
            # A consumed tool changes during provenance validation.
            def drift(evidence,verification,output,consume):
                path=root/'input.txt';path.write_text('before');consume(path);path.write_text('after')
                raise ValueError('synthetic failure')
            with patch.object(p,'provenance',side_effect=drift): result=p.prepare(evidence,root/'missing.json',out)
            self.assertEqual(result['integrity_failure'],'input drift');p.o.check_output(out)


if __name__=='__main__':unittest.main()
