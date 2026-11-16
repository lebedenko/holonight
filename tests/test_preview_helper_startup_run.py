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
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
r=module('helper_run_test','run-preview-helper-startup.py')
f=module('helper_report_test','report-preview-helper-startup.py')
i=module('helper_independent_test','verify-preview-helper-startup-run.py')
h=module('helper_host_test','verify-preview-helper-startup-host.py')
b=module('helper_rebind_test','rebind-preview-helper-startup.py')


def event(span,ns,edge,operation='preparation',parent=None):
    return dict(version=1,ns=ns,pid=10,tid=11,invocation='test',host='host',boot='boot',clock='CLOCK_MONOTONIC',
                service=1,observation=1,job=2,worker=3,preparation=4,request_generation=5,runtime_generation=None,
                span=span,parent=parent,operation=operation,edge=edge,outcome='unavailable' if edge=='begin' else 'returned')
CLOCK=dict(name='CLOCK_MONOTONIC',provenance=dict(host='host',boot_id='boot'))


class HelperRunTests(unittest.TestCase):
    def setUp(self):
        # Synthetic tests must never spawn a compiler, recorder or workload.
        self.guards=[patch('subprocess.run',side_effect=AssertionError('process execution disabled')),
                     patch('subprocess.Popen',side_effect=AssertionError('process execution disabled'))]
        for guard in self.guards: guard.start();self.addCleanup(guard.stop)

    def test_exact_schedule_and_binary_sharing(self):
        self.assertEqual(r.v.protocol()['schedule'],i.protocol())
        commands=r.planned_commands(Path('/built'),Path('/run/private'),Path('/evidence/observations'))
        self.assertEqual(len(commands),36)
        self.assertEqual(len({e['identity'] for e in commands}),36)
        for variant in ('A','C'):
            binaries={e['argv'][0] for e in commands if e['invocation']['variant']==variant and e['invocation']['arm']!='baseline'}
            self.assertEqual(len(binaries),1)

    def test_each_failure_stops_before_next_launch(self):
        commands=r.planned_commands(Path('/built'),Path('/run/private'),Path('/evidence/observations'))
        for failure in ('integrity','before','launch','account','count','post_integrity'):
            with self.subTest(failure=failure),tempfile.TemporaryDirectory() as tmp:
                launches=[];checks=[]
                def fail(): raise ValueError('injected '+failure)
                def integrity():
                    checks.append(1)
                    if failure=='integrity' or failure=='post_integrity' and len(checks)>1: fail()
                def before(target):
                    if failure=='before': fail()
                def launch(index,entry):
                    launches.append(index)
                    if failure=='launch': fail()
                    return {}
                def account(index,entry,process):
                    if failure=='account': fail()
                    return [] if failure=='count' else [{}]
                result=dict(invocations=[],warmup_observations=0,measured_observations=0)
                with self.assertRaises(ValueError):r.run_schedule(commands,Path(tmp),result,integrity,before,launch,account)
                self.assertEqual(launches,[] if failure in ('integrity','before') else [0])

    def test_schedule_drift_prevents_any_launch(self):
        commands=r.planned_commands(Path('/built'),Path('/run/private'),Path('/evidence/observations'))
        commands[0]['invocation']=dict(commands[0]['invocation'],observations=2)
        def forbidden(*args):self.fail('launched altered protocol')
        with self.assertRaisesRegex(ValueError,'scheduled'):r.run_schedule(commands,Path('/unused'),{},forbidden,forbidden,forbidden,forbidden)

    def test_invocation_identity_survives_root_session_environment(self):
        entry=dict(identity='unique',argv=['binary','runtime','fixture','startup','1','out.json'])
        with tempfile.TemporaryDirectory() as tmp:
            entry['argv'][-1]=str(Path(tmp)/'out.json')
            def execute(argv,target,env,credentials,timeout):
                self.assertEqual(env['HOLONIGHT_HELPER_INVOCATION'],'unique')
                self.assertEqual(credentials,dict(user=1000));self.assertEqual(timeout,12)
                return dict(exit=0)
            with patch.object(r.r,'session',return_value=({'PATH':'/usr/bin'},dict(user=1000))),patch.object(r.o.gate.smoke,'execute',side_effect=execute):
                self.assertEqual(r.workload(entry,12),dict(exit=0))

    def test_decimal_strings_are_normalized_before_scheduler_identity(self):
        events=[event(1,10,'begin'),event(1,90,'end')]
        for e in events:
            for name in ('ns',*f.a.NUMBERS):
                if e[name] is not None:e[name]=str(e[name])
        parsed,issues=f.a.parse('\n'.join('HELPER_STARTUP '+json.dumps(e) for e in events),'synthetic')
        self.assertFalse(issues);self.assertEqual([e['ns'] for e in parsed],[10,90])
        f.strict_boundaries(parsed,'test',CLOCK)

    def test_host_boot_invocation_and_outcome_mismatch(self):
        for key,value in [('host','machine-id'),('boot','other'),('invocation',None),('outcome','returned')]:
            records=[event(1,0,'begin'),event(1,100,'end')];records[0][key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):f.strict_boundaries(records,'test',CLOCK)

    def test_thread_nesting_missing_boundary_and_cross_thread_failure(self):
        records=[event(1,0,'begin'),event(2,10,'begin','launcher_checks',1),event(2,30,'end','launcher_checks',1),event(1,50,'end')]
        f.strict_boundaries(records,'test',CLOCK)
        cases=[records[:-1],[records[0],records[1],records[3],records[2]],
               [records[0],dict(records[1],tid=22),records[2],records[3]]]
        for bad in cases:
            with self.assertRaises(ValueError):f.strict_boundaries(bad,'test',CLOCK)

    def test_missing_source_operations_and_exception_reached_scopes(self):
        begin=event(1,0,'begin');end=event(1,100,'end')
        window=dict(begin=begin,end=end,spans=[])
        with self.assertRaisesRegex(ValueError,'operations'):f.required_operations(window,'A')
        window['end']=dict(end,outcome='exception')
        f.required_operations(window,'A')

    def test_setup_standby_selected_demand_are_separate(self):
        begin=event(1,10,'begin');end=event(1,90,'end');window=dict(begin=begin,end=end)
        legacy=dict(phase='helper_prepare',start=0,stop=100,begin=begin,end=end)
        for classification in ('setup','standby','demand'):
            span=dict(legacy,cause='setup_activity') if classification=='setup' else dict(legacy,role=classification)
            lifecycle=dict(accounting=[] if classification=='setup' else [dict(timeline=[span])],
                           unassigned=[span] if classification=='setup' else [])
            selected=[dict(begin,phase='selected_worker')]
            self.assertEqual(f.bind_lifecycle(window,lifecycle,selected)['classification'],classification)
            if classification=='demand':
                with self.assertRaises(ValueError):f.bind_lifecycle(window,lifecycle,[])
        with self.assertRaises(ValueError):f.bind_lifecycle(window,dict(accounting=[],unassigned=[]),[])

    def test_bookkeeping_after_v3_boundary_uses_exact_identities(self):
        begin=event(1,10,'begin');end=event(1,110,'end')
        legacy=dict(phase='helper_prepare',start=0,stop=100,begin=begin,end=end,role='demand')
        lifecycle=dict(accounting=[dict(timeline=[legacy])],unassigned=[])
        selected=[dict(begin,phase='selected_worker')]
        result=f.bind_lifecycle(dict(begin=begin,end=end),lifecycle,selected)
        self.assertEqual(result['supplemental_after_legacy_ns'],10)
        with self.assertRaises(ValueError):
            f.bind_lifecycle(dict(begin=dict(begin,worker=99),end=end),lifecycle,selected)

    def test_oneshot_uses_explicit_demand_job_with_unavailable_preparation(self):
        begin=event(1,10,'begin');begin['preparation']=None
        end=dict(begin,edge='end',ns=110,outcome='returned')
        legacy=dict(phase='helper_prepare',start=0,stop=100,begin=dict(begin,preparation=0),
                    end=dict(end,preparation=0),role='demand')
        lifecycle=dict(accounting=[dict(timeline=[legacy])],unassigned=[])
        dispatch=dict(begin,phase='demand_dispatch',preparation=0)
        result=f.bind_lifecycle(dict(begin=begin,end=end),lifecycle,[dispatch])
        self.assertEqual(result['classification'],'demand')
        self.assertIsNone(result['runtime_generation'])
        with self.assertRaises(ValueError):
            f.bind_lifecycle(dict(begin=begin,end=end),lifecycle,[dict(dispatch,job=99)])

    def test_scheduler_identity_loss_lifetime_unknown_and_coverage_fail(self):
        events=[event(1,10,'begin'),event(1,90,'end')]
        parsed,_=f.a.parse('\n'.join('HELPER_STARTUP '+json.dumps(e) for e in events),'synthetic')
        span=dict(begin=parsed[0],start=10,stop=90)
        capture=dict(version=2,clock=CLOCK,start_ns=0,stop_ns=100,export_complete=True,events=[],
                     tasks=[dict(key=[10,11,1],start_ns=0,stop_ns=100,initial='running',cpu=0,identity_evidence=parsed)])
        self.assertTrue(f.a.scheduler_span(span,capture)['available'])
        for failure in ('host','boot','loss','lifetime','ambiguous','unknown','identity','export'):
            bad=copy.deepcopy(capture)
            if failure in ('host','boot'):bad['clock']['provenance']['host' if failure=='host' else 'boot_id']='other'
            if failure=='loss':bad['events']=[dict(kind='loss',ns=50,count=1)]
            if failure=='lifetime':bad['tasks'][0]['stop_ns']=80
            if failure=='ambiguous':bad['tasks']*=2
            if failure=='unknown':bad['tasks'][0]['initial']='unknown'
            if failure=='identity':bad['tasks'][0]['identity_evidence']=[]
            if failure=='export':bad['export_complete']=False
            with self.subTest(failure=failure):self.assertFalse(f.a.scheduler_span(span,bad)['available'])

    def test_timeout_uses_remaining_budget_and_retains_cleanup_failure(self):
        # Recorder supervision is reused unchanged; verify its finally path with a fake boundary.
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            with patch.object(r.r.subprocess,'Popen',side_effect=OSError('recorder unavailable')):
                with self.assertRaises(OSError):r.r.capture(path,lambda remaining:self.fail('workload launched'))
            self.assertTrue((path/'recording-partial.json').is_file())
            self.assertTrue(json.loads((path/'recording-partial.json').read_text())['cleanup']['not_started'])

    def test_blocked_action_is_sealed_collision_and_drift_preserved(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            root=Path(tmp);source=root/'input';source.mkdir();(source/'file').write_text('before')
            out=root/'output'
            def fail(result):raise ValueError('injected preflight failure')
            with patch.object(r,'identities',return_value={}):result=r.action(out,[source],fail)
            self.assertEqual(result['status'],'blocked');r.o.check_output(out)
            self.assertEqual(r.read(out/'unexecuted-schedule.json'),i.protocol())
            before=r.o.inventory(out)
            with patch.object(r,'identities',return_value={}),self.assertRaises(ValueError):r.action(out,[source],fail)
            self.assertEqual(r.o.inventory(out),before)
            def drift(result):(source/'file').write_text('after')
            with patch.object(r,'identities',return_value={}):result=r.action(root/'drift',[source],drift)
            self.assertEqual(result['integrity_failure'],'input/tool drift');r.o.check_output(root/'drift')

    def test_independent_raw_source_and_interval_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); trace=root/'trace.stderr'; source=root/'source.cpp'
            source.write_text('HelperStartupTrace::Scope root("preparation");\n')
            trace.write_text('\n'.join('HELPER_STARTUP '+json.dumps(e) for e in
                            [event(1,10,'begin'),event(1,90,'end')]))
            records,issues=f.a.parse(trace.read_text(),str(trace));self.assertFalse(issues)
            span=dict(pid=10,span=1,parent=None,operation='preparation',start=10,stop=90,inclusive_ns=80,
                      child_union=[],exclusive_intervals=[[10,90]],exclusive_ns=80,scheduler=dict(available=False),
                      source_citations=[dict(file=str(source),sha256=i.digest(source),line=1,text=source.read_text().strip())])
            account=dict(records=records,population=dict(invocation='test'),spans=[span],windows=[])
            i.arithmetic(account)
            bad=copy.deepcopy(account);bad['spans'][0]['exclusive_ns']=79
            with self.assertRaisesRegex(ValueError,'exclusive'):i.arithmetic(bad)
            bad=copy.deepcopy(account);bad['records'][0]['job']=99
            with self.assertRaisesRegex(ValueError,'raw helper'):i.arithmetic(bad)
            source.write_text('changed\n')
            with self.assertRaisesRegex(ValueError,'source'):i.arithmetic(account)

    def test_host_revision_requires_exact_old_new_hashes_and_protocol(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);old=root/'original';new=root/'revision';old.mkdir();new.mkdir()
            paths=[root/f'host-{n}' for n in range(4)]
            for path in paths:path.write_text('old')
            consumed={str(path):i.digest(path) for path in paths}
            r.write(old/'integrity.json',dict(passed=True,checks=dict(input=True),before={},consumed=consumed))
            for name in ('protocol.json','anchors.json','inputs.json','provenance.json','fixtures.json','source-comparison.json'):
                (old/name).write_text('{}\n');(new/name).write_text('{}\n')
            r.o.seal(old)
            verification=old.parent/(old.name+'-independent.json')
            r.write(verification,dict(status='passed',preparation_seal=i.digest(old/'seal.json')))
            changes={}
            for path in paths:
                path.write_text('new');changes[str(path)]=dict(old=consumed[str(path)],new=i.digest(path))
            tools={str(ROOT/'scripts'/name):i.digest(ROOT/'scripts'/name) for name in
                   ('rebind-preview-helper-startup.py','verify-preview-helper-startup-host.py')}
            (new/'tools').mkdir()
            for name in tools:(new/'tools'/Path(name).name).write_bytes(Path(name).read_bytes())
            binding=dict(original=str(old),original_seal=i.digest(old/'seal.json'),
                         original_verification_sha256=i.digest(verification),changes=changes,tools=tools)
            r.write(new/'host-rebind.json',binding)
            r.write(new/'integrity.json',dict(consumed=dict({name:change['new'] for name,change in changes.items()},**tools),
                                            before={str(old):i.inventory(old)}))
            with patch.object(h,'HOST_PATHS',tuple(map(str,paths))):
                h.host_binding(new)
                (new/'protocol.json').write_text('{"changed":true}\n')
                with self.assertRaisesRegex(ValueError,'protocol'):h.host_binding(new)
                (new/'protocol.json').write_text('{}\n')
                paths[0].write_text('drift')
                with self.assertRaisesRegex(ValueError,'host input drift'):h.host_binding(new)

    def test_rebind_rejects_unexpected_input_drift_and_seals_failure(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            root=Path(tmp);original=root/'original';original.mkdir();host=root/'unexpected'
            host.write_text('before');expected=i.digest(host);host.write_text('after')
            r.write(original/'integrity.json',dict(consumed={str(host):expected}))
            r.o.seal(original);before=i.inventory(original)
            result=b.rebind(original,root/'revision')
            self.assertEqual(result['status'],'blocked')
            self.assertIn('unexpected changed inputs',result['failure'])
            r.o.check_output(root/'revision');self.assertEqual(i.inventory(original),before)

    def test_unrelated_scheduler_startup_issues_do_not_reject_complete_target(self):
        events=[event(1,10,'begin'),event(1,90,'end')]
        span=dict(begin=events[0],start=10,stop=90)
        capture=dict(version=2,clock=CLOCK,start_ns=0,stop_ns=100,export_complete=True,diagnostics=[],
                     tasks=[dict(key=[10,11,1],start_ns=0,stop_ns=100,initial='running',cpu=0,identity_evidence=events),
                            dict(key=[20,21,1],start_ns=0,stop_ns=100,initial='unknown'),
                            dict(key=[0,0,1],start_ns=0,stop_ns=100,initial='unknown')],
                     events=[dict(kind='switch',ns=40,cpu=1,prev=[20,21,1],next=[0,0,1],prev_state='non_runnable')])
        issues=f.bind_scheduler([span],capture)
        self.assertIn('missing switch transition',issues)
        self.assertTrue(span['scheduler']['available'])
        self.assertEqual(span['scheduler']['totals']['running'],80)
        bad=copy.deepcopy(capture);bad['tasks'][0]['initial']='unknown'
        f.bind_scheduler([span],bad);self.assertFalse(span['scheduler']['available'])
        bad=copy.deepcopy(capture);bad['events'].append(dict(kind='loss',ns=50,count=1))
        with self.assertRaisesRegex(ValueError,'loss'):f.bind_scheduler([span],bad)
        bad=copy.deepcopy(capture);bad['export_complete']=False
        with self.assertRaisesRegex(ValueError,'incomplete'):f.bind_scheduler([span],bad)

    def test_effects_use_only_signed_block_medians(self):
        summary=[dict(variant=v,endpoint=e,block=b,arm=arm,latency_ns=dict(median=100+b+offset))
                 for v in ('A','C') for e in ('pixels','metadata') for b in range(5)
                 for arm,offset in (('baseline',20),('instrumented',10),('captured',0))]
        self.assertTrue(all(row['signed_block_median_difference_ns']==-10 for row in f.effects(summary)))


if __name__=='__main__':unittest.main()
