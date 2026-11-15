import copy
from contextlib import ExitStack
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validation_prepare',ROOT/'scripts/prepare-preview-validation.py')
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)


class ValidationPreparationTests(unittest.TestCase):
    def setUp(self):
        stack=ExitStack(); self.addCleanup(stack.close)
        for name in ('subprocess.Popen','subprocess.run','os.system','os.popen','os.fork','os.posix_spawn'):
            stack.enter_context(patch(name,side_effect=AssertionError('process launch forbidden')))

    def test_schedule_has_exact_budget_and_each_block_contains_all_combinations(self):
        rows=v.schedule()
        self.assertEqual(len(rows),66)
        self.assertEqual(sum(r['observations'] for r in rows),606)
        self.assertEqual(sum(r['observations'] for r in rows if not r['warmup']),600)
        self.assertEqual([(r['variant'],r['arm']) for r in rows[:6]],v.COMBINATIONS)
        for block in range(10):
            selected=[r for r in rows if r['block']==block]
            self.assertEqual(len(selected),6)
            offset=block%6
            expected=v.COMBINATIONS[offset:]+v.COMBINATIONS[:offset]
            if block%2: expected.reverse()
            self.assertEqual([(r['variant'],r['arm']) for r in selected],expected)
            self.assertTrue(all(r['observations']==10 and r['fixture']=='3200x2400.png' for r in selected))
        for variant,arm in v.COMBINATIONS:
            self.assertEqual(sum(r['observations'] for r in rows if not r['warmup'] and (r['variant'],r['arm'])==(variant,arm)),100)

    def test_literal_probe_replay_preserves_every_original_byte(self):
        for name in ('verification','generation'):
            source=(ROOT/'tests/fixtures/preview-validation'/(name+'.cpp')).read_text()
            generated,anchors=v.instrument(source,'source/'+name+'.cpp')
            restored=generated
            for anchor in reversed(anchors):
                self.assertEqual(restored.count(anchor['replacement']),1)
                restored=restored.replace(anchor['replacement'],anchor['anchor'],1)
            self.assertEqual(restored,source)
            self.assertEqual(generated.count('ValidationTrace::Scope validation_root'),1)
            self.assertEqual(generated.count('throw '),source.count('throw '))
            for text in ('hash.addData(&file)','QCryptographicHash::Sha256','manifest.readAll()',
                         'selector(base.get(), afterSelector) != name || !same(selectedIdentity, afterSelector) ||'):
                self.assertEqual(generated.count(text),source.count(text))
            for anchor in anchors:
                with self.subTest(name=name,anchor=anchor['anchor'][:60]):
                    # Missing or duplicate original anchors must be refused, never guessed.
                    with self.assertRaises(ValueError):
                        v.replace('',anchor['anchor'],anchor['replacement'],[],'fixture')
                    with self.assertRaises(ValueError):
                        v.replace(anchor['anchor']*2,anchor['anchor'],anchor['replacement'],[],'fixture')

    def test_hash_condition_preserves_short_circuit_and_combined_read(self):
        source=(ROOT/'tests/fixtures/preview-validation/verification.cpp').read_text()
        generated,_=v.instrument(source,'source/verification.cpp')
        self.assertIn('return file.open(QIODevice::ReadOnly); }) || !ValidationTrace::measure("read_hash", ordinal, [&] { return hash.addData(&file); }) ||',generated)
        self.assertIn('return QString::fromLatin1(hash.result().toHex()) != record["sha256"].toString(); })',generated)
        self.assertIn('const auto ordinal = validation_ordinal++;',generated)
        self.assertNotIn('file.readAll()',generated)

    def test_blocked_provenance_preserves_and_seals_failure(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence=root/'evidence'; evidence.mkdir()
            v.write(evidence/'assessment.json',dict(status='blocked')); v.o.seal(evidence)
            before=v.o.inventory(evidence)
            result=v.prepare(evidence,root/'output')
            self.assertEqual(result['status'],'blocked')
            self.assertEqual(result['stage'],'provenance')
            self.assertIn('predecode evidence blocked',result['failure'])
            self.assertEqual(result['launched_invocations'],0)
            self.assertEqual(v.o.inventory(evidence),before)
            v.o.check_output(root/'output')
            self.assertFalse((root/'output/baseline').exists())

    def test_destination_reuse_and_symlink_are_refused(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence=root/'evidence'; evidence.mkdir()
            with self.assertRaises(ValueError): v.prepare(evidence,evidence)
            link=root/'link'; link.symlink_to(evidence)
            with self.assertRaises(ValueError): v.prepare(evidence,link)



spec=importlib.util.spec_from_file_location('validation_report_tests',ROOT/'scripts/report-preview-validation.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
r=a.r


def event(operation,span,parent,ns,edge='begin',validation=1,ordinal=-1):
    return dict(version=1,pid=10,tid=11,service=20,observation=1,job=None,worker=None,preparation=None,
                validation=validation,span=span,parent=parent,ordinal=ordinal,operation=operation,
                ns=ns,edge=edge,outcome='unavailable' if edge=='begin' else 'returned')


def validation_events():
    return [event('runtime',1,0,0),event('manifest_parse',2,1,1),event('manifest_read',3,2,2),
            event('manifest_read',3,2,7,'end'),event('manifest_parse',2,1,10,'end'),
            event('read_hash',4,1,20),event('read_hash',4,1,80,'end'),event('runtime',1,0,100,'end')]


def measured_row(variant,arm,index,duration=100):
    selected=a.spans(validation_events())
    row=dict(variant=variant,arm=arm,invocation_index=index,observation=1,block=0,warmup=False,
             start_ns=0,stop_ns=100,duration_ns=100,largest_uncovered_ns=10,
             endpoints={e:dict(harness_latency_ns=200) for e in ('pixels','metadata')})
    if arm!='baseline':
        row['validation']=a.intervals(selected,0,duration)
        if arm=='captured':
            row['validation']['scheduler_groups']={n:dict(running=ns,runnable=0,non_runnable=0,unknown=0)
                                                  for n,ns in row['validation']['groups_ns'].items()}
    return row


class ValidationAccountingTests(unittest.TestCase):
    setUp=ValidationPreparationTests.setUp
    def test_span_pairing_nesting_and_exceptional_exits(self):
        events=validation_events(); events[-1]['outcome']='exception'
        selected=a.spans(events)
        self.assertEqual(len(selected),4)
        self.assertEqual(selected[0]['end']['outcome'],'exception')
        for change in ('missing','duplicate','parent','context','thread','clock'):
            bad=copy.deepcopy(events)
            if change=='missing': bad.pop()
            if change=='duplicate': bad.append(bad[-1])
            if change=='parent': bad[2]['parent']=1
            if change=='context': bad[-1]['service']=99
            if change=='thread': bad[-1]['tid']=99
            if change=='clock': bad[3]['ns']=0
            with self.subTest(change=change),self.assertRaises(ValueError): a.spans(bad)

    def test_nested_roots_get_independent_validation_identities(self):
        events=[event('generation',1,0,0),event('nested_runtime',2,1,1),
                event('runtime',3,2,2,validation=3),event('runtime',3,2,3,'end',validation=3),
                event('nested_runtime',2,1,4,'end'),event('generation',1,0,5,'end')]
        self.assertEqual(len(a.spans(events)),3)
        events[2]['validation']=1
        with self.assertRaises(ValueError): a.spans(events)

    def test_disjoint_leaves_union_and_parent_subtraction(self):
        selected=a.spans(validation_events()); part=a.intervals(selected,0,100)
        self.assertEqual(part['groups_ns'],dict(runtime_outside_children=31,manifest_parse=4,manifest_read=5,read_hash=60))
        self.assertEqual(part['unions']['runtime']['covered_ns'],100)
        self.assertEqual(part['inclusive_ns'],174)
        self.assertEqual(part['parent_outside_nested'][0]['duration_ns'],31)
        self.assertEqual(sum(part['groups_ns'].values()),100)
        clipped=a.intervals(selected,5,85)
        self.assertEqual(sum(clipped['groups_ns'].values()),80)
        self.assertEqual(clipped['unions']['manifest_read']['covered_ns'],2)

    def test_uncovered_and_cross_thread_sets_remain_nonadditive(self):
        selected=a.spans(validation_events())
        extra=a.spans([dict(e,pid=12,tid=13,service=21) for e in validation_events()])
        part=a.intervals(selected+extra,-5,105)
        self.assertEqual(part['groups_ns']['uncovered'],10)
        self.assertEqual(sum(part['groups_ns'].values()),110)
        self.assertEqual(part['inclusive_ns'],348)

    def test_manifest_mapping_and_file_children_are_exact(self):
        mapping=r.ordinal_mapping(dict(files=[dict(path='usr/a',size=12,sha256='a'*64),dict(path='usr/b',size=13,sha256='b'*64)]))
        events=[event('runtime',1,0,0)]
        for ordinal in range(2):
            file=ordinal*10+2
            events.append(event('file',file,1,ordinal*20+1,ordinal=ordinal))
            for index,name in enumerate(('record_prepare','attributes','file_open','read_hash','digest_compare')):
                token=file+index+1; start=ordinal*20+index*2+2
                events.extend([event(name,token,file,start,ordinal=ordinal),event(name,token,file,start+1,'end',ordinal=ordinal)])
            events.append(event('file',file,1,ordinal*20+15,'end',ordinal=ordinal))
        events.append(event('runtime',1,0,50,'end'))
        selected=a.spans(events)
        self.assertEqual([x['size'] for x in a.mapped_files(selected,mapping)],[12,13])
        with self.assertRaises(ValueError): a.mapped_files(selected,mapping[:1])
        bad=copy.deepcopy(selected); bad[1]['begin']['parent']=99
        with self.assertRaises(ValueError): a.mapped_files(bad,mapping)
        for manifest in (dict(files=[dict(path='../x',size=1)]),dict(files=[dict(path='usr/x',size=-1)])):
            with self.assertRaises(ValueError): r.ordinal_mapping(manifest)

    def test_distributions_use_observations_and_zero_missing_groups(self):
        rows=[measured_row(variant,arm,index) for index,(variant,arm) in enumerate(v.COMBINATIONS)]
        other=copy.deepcopy(rows[2]); other['invocation_index']=99
        other['validation']['groups_ns']['new_group']=0
        rows.append(other)
        summary=a.summarize(rows)
        cell=next(c for c in summary if c['variant']=='A' and c['arm']=='validation' and c['block']=='pooled')
        self.assertEqual(cell['observations'],2)
        self.assertEqual(cell['groups']['read_hash']['duration_ns']['count'],2)
        self.assertEqual(cell['groups']['new_group']['duration_ns']['median'],0)
        self.assertEqual(a.rankings(summary)[0]['order'][0],'read_hash')
        self.assertEqual(a.stats(list(range(1,101))),dict(count=100,minimum=1,median=50.5,p95=95,maximum=100))

    def test_rankings_have_deterministic_label_tiebreaks(self):
        rows=[measured_row(variant,arm,index) for index,(variant,arm) in enumerate(v.COMBINATIONS)]
        for row in rows:
            if 'validation' in row: row['validation']['groups_ns']=dict(z=50,a=50)
        ranks=a.rankings(a.summarize(rows))
        self.assertEqual(ranks[0]['order'],['a','z'])
        self.assertEqual(ranks[1]['order'],['a','z'])

    def test_all_cutoff_median_and_gap_ties_are_retained(self):
        rows=[measured_row(variant,arm,index*10+j) for index,(variant,arm) in enumerate(v.COMBINATIONS) for j in range(7)]
        chosen=a.selections(rows)
        self.assertEqual(len(chosen),42)
        self.assertTrue(all('predecode_slowest_five_with_ties' in r['selection_reasons'] and
                            'predecode_nearest_median_with_ties' in r['selection_reasons'] and
                            'predecode_largest_uncovered_with_ties' in r['selection_reasons'] for r in chosen))
        comparison=a.comparisons(chosen,a.rankings(a.summarize(rows)))
        self.assertTrue(all(c['order'][0]=='read_hash' for c in comparison))

    def test_scheduler_lifetimes_states_and_group_totals(self):
        selected=a.spans(validation_events())
        clock=dict(name='CLOCK_MONOTONIC',provenance='test-boot')
        capture=dict(version=1,clock=clock,start_ns=0,stop_ns=101,tasks=[
            dict(key=[10,11,1],start_ns=0,stop_ns=101,initial='running',cpu=0),
            dict(key=[12,12,1],start_ns=0,stop_ns=101,initial='runnable')],events=[
            dict(kind='switch',ns=30,cpu=0,prev=[10,11,1],next=[12,12,1],prev_state='non_runnable'),
            dict(kind='wakeup',ns=50,cpu=0,task=[10,11,1]),
            dict(kind='switch',ns=70,cpu=0,prev=[12,12,1],next=[10,11,1],prev_state='non_runnable')])
        result=a.scheduler_windows(selected,capture,clock)
        root=next(w for w in result['windows'] if w['span']==1)
        self.assertEqual(root['totals'],dict(running=60,runnable=20,non_runnable=20,unknown=0))
        groups=a.scheduler_groups(a.intervals(selected,0,100),result)
        self.assertEqual(groups['read_hash'],dict(running=20,runnable=20,non_runnable=20,unknown=0))
        self.assertEqual(sum(sum(v.values()) for v in groups.values()),100)
        for change in ('clock','missing','ambiguous','unknown','loss'):
            bad=copy.deepcopy(capture)
            if change=='clock': bad['clock']=dict(name='CLOCK_MONOTONIC',provenance='other')
            if change=='missing': bad['tasks'][0]['key']=[99,99,1]
            if change=='ambiguous': bad['tasks'].append(dict(bad['tasks'][0],key=[10,11,2]))
            if change=='unknown': bad['tasks'][0]['initial']='unknown'
            if change=='loss': bad['events'].append(dict(kind='loss',ns=90,count=1))
            with self.subTest(change=change),self.assertRaises(ValueError): a.scheduler_windows(selected,bad,clock)

    def test_historical_seal_allows_appended_evidence_but_no_sealed_edits(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); (root/'source').write_text('sealed')
            v.o.seal(root)
            (root/'later-execution.json').write_text('{}')
            v.verify_seal(root,exact=False)
            with self.assertRaises(ValueError): v.verify_seal(root)
            (root/'source').write_text('changed')
            with self.assertRaisesRegex(ValueError,'sealed file drift'): v.verify_seal(root,exact=False)

    def test_failed_action_seals_partial_evidence_and_detects_input_drift(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); source=root/'source'; source.mkdir(); (source/'input').write_text('before')
            def fail(result):
                (root/'out/partial').write_text('retained')
                (source/'input').write_text('after')
                raise ValueError('first gate failed')
            result=r.action(root/'out',[source],fail)
            self.assertEqual(result['status'],'blocked')
            self.assertIn('first gate failed',result['failure'])
            self.assertIn('integrity_failure',result)
            self.assertEqual((root/'out/partial').read_text(),'retained')
            v.o.check_output(root/'out')

    def test_blocked_preparation_prevents_build_and_report_launches(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); prepared=root/'prepared'; prepared.mkdir()
            v.write(prepared/'assessment.json',dict(status='blocked')); v.o.seal(prepared)
            result=r.build(prepared,root/'build')
            self.assertEqual(result['status'],'blocked')
            self.assertIn('preparation blocked',result['failure'])
            self.assertFalse((root/'build/commands.json').exists())
            v.o.check_output(root/'build')


def preparation_fixture(root):
    origin=root/'origin'; prepared=root/'matched'; qualification=root/'qualification'; evidence=root/'evidence'
    for path in (origin,prepared,qualification,evidence): path.mkdir()
    pairs={}
    for key in ('AU','AT','CT'):
        base=origin/key
        (base/'source').mkdir(parents=True); (base/'harness-source').mkdir()
        names=('verification','generation') if key=='CT' else ('verification',)
        for name in names:
            relative='holonight-images/src/isolated/'+name+'.cpp'
            path=base/'source'/relative; path.parent.mkdir(parents=True,exist_ok=True)
            text=(ROOT/'tests/fixtures/preview-validation'/(name+'.cpp')).read_bytes()
            if key=='AU': text=v.p.reconstruct_v3(text)
            path.write_bytes(text)
        (base/'harness-source/main.cpp').write_text('QCoreApplication app(argc, argv);\n')
        pairs[key]={group:v.o.inventory(base/group) for group in v.GROUPS}
    diff=[]
    for group in v.GROUPS:
        for name in pairs['AU'][group]:
            left,right=origin/'AU'/group/name,origin/'AT'/group/name
            if left.read_bytes()!=right.read_bytes():
                diff+=v.difflib.unified_diff(left.read_text().splitlines(True),right.read_text().splitlines(True),fromfile=str(left),tofile=str(right))
    (origin/'A-tracing.diff').write_text(''.join(diff))
    v.write(origin/'preparation.json',dict(pairs=pairs,retained_unchanged=True,equivalence={'A':{'source':[]}}))
    v.o.seal(origin)
    outputs={}
    for mode in ('v3','v4'):
        for variant in ('A','C'):
            base=prepared/mode/variant; base.mkdir(parents=True)
            (base/'trace.h').write_text('// frozen\n')
            for group in v.GROUPS: r.shutil.copytree(origin/(variant+'T')/group,base/group)
            v.write(base/'source-inventory.json',{group:v.o.inventory(base/group) for group in v.GROUPS})
            outputs[mode+'/'+variant]=v.o.inventory(base)
    v.write(prepared/'manifest.json',dict(status='prepared',issues=[],inputs=dict(v3=str(origin)),outputs=outputs))
    before={str(origin/'seal.json'):v.o.digest(origin/'seal.json')}
    v.write(prepared/'input-integrity.json',dict(unchanged=True,before=before,after=before))
    v.write(prepared/'anchor-review.json',{'A':[],'C':[]})
    v.o.seal(prepared)
    r.shutil.copytree(origin/'AU/source',qualification/'A/source')
    v.write(qualification/'freeze.json',dict(source_inventories={'A':v.o.inventory(qualification/'A/source')}))
    fixture=root/'fixtures'; fixture.mkdir(); (fixture/'3200x2400.png').write_bytes(b'frozen fixture')
    consumed={str(prepared/name):digest for name,digest in v.o.inventory(prepared).items()}
    consumed[str(fixture/'3200x2400.png')]=v.o.digest(fixture/'3200x2400.png')
    v.write(evidence/'integrity.json',dict(passed=True,consumed=consumed))
    v.write(evidence/'assessment.json',dict(status='complete'))
    v.write(evidence/'source-comparison.json',dict(chain=[str(prepared/'v4/A/source'),None,None,None,str(qualification/'A/source')]))
    v.o.seal(evidence)
    return evidence,fixture,prepared


class ValidationSourceRegressions(unittest.TestCase):
    setUp=ValidationPreparationTests.setUp

    def test_full_preparation_and_independent_byte_replay_without_processes(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence,fixture,prepared=preparation_fixture(root)
            with patch.object(v.o.old,'FIXTURE_ROOT',fixture):
                result=v.prepare(evidence,root/'output')
            self.assertEqual(result['status'],'prepared',result)
            self.assertEqual(v.read(root/'output/source-comparison.json')['status'],'equivalent')
            self.assertTrue(v.verify_generated(root/'output',prepared))
            v.o.check_output(root/'output')
            self.assertNotIn('ValidationTrace::',(root/'output/baseline/A/trace.h').read_text())
            self.assertIn('namespace ValidationTrace',(root/'output/validation/A/trace.h').read_text())
            path=root/'output/validation/C/source/holonight-images/src/isolated/generation.cpp'
            path.write_text(path.read_text().replace('return false;','return true;'))
            with self.assertRaisesRegex(ValueError,'transformation mismatch'): v.verify_generated(root/'output',prepared)

    def test_frozen_source_drift_blocks_before_any_output_source_tree(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence,fixture,prepared=preparation_fixture(root)
            path=prepared/'v4/C/source/holonight-images/src/isolated/verification.cpp'
            path.write_text(path.read_text()+'// drift\n')
            with patch.object(v.o.old,'FIXTURE_ROOT',fixture): result=v.prepare(evidence,root/'output')
            self.assertEqual(result['status'],'blocked')
            self.assertEqual(result['stage'],'provenance')
            self.assertFalse((root/'output/validation').exists())
            v.o.check_output(root/'output')




class ValidationExecutionRegressions(unittest.TestCase):
    setUp=ValidationPreparationTests.setUp

    def state(self):
        return dict(invocations=[],launched=0,unexecuted=66,measured_observations=0,warmup_observations=0)

    def test_first_accounting_failure_leaves_remaining_schedule_unexecuted(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            output=Path(temp); commands=r.planned_commands(output/'built',output/'runtime',output/'observations')
            launched=[]; result=self.state()
            def launch(index,entry): launched.append(index); return dict(exit=0)
            def account(index,entry,process):
                if index==1: raise ValueError('accounting gate failed')
                return [dict(valid=True)]*entry['invocation']['observations']
            with self.assertRaisesRegex(ValueError,'accounting gate failed'):
                r.run_schedule(commands,output,result,lambda:None,lambda target:None,launch,account)
            self.assertEqual(launched,[0,1])
            self.assertEqual(result['unexecuted'],64)
            self.assertEqual(result['warmup_observations'],1)
            self.assertEqual(result['invocations'][-1]['status'],'failed')
            self.assertEqual(v.read(output/'progress.json')['launched'],2)

    def test_initial_integrity_failure_launches_nothing_and_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            output=Path(temp); commands=r.planned_commands(output/'built',output/'runtime',output/'observations')
            result=self.state()
            def forbidden(*args): raise AssertionError('unexpected workload')
            def failure(): raise ValueError('integrity gate failed')
            with self.assertRaisesRegex(ValueError,'integrity gate failed'):
                r.run_schedule(commands,output,result,failure,forbidden,forbidden,forbidden)
            self.assertEqual(result,self.state())
            commands[0]['invocation']['fixture']='other.png'
            with self.assertRaisesRegex(ValueError,'scheduled invocation drift'):
                r.run_schedule(commands,output,result,lambda:None,forbidden,forbidden,forbidden)

    def test_exact_schedule_completion_and_pre_registered_commands(self):
        import contextlib
        import io
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            output=Path(temp); commands=r.planned_commands(output/'built',output/'runtime',output/'observations')
            result=self.state(); launches=[]
            def launch(index,entry): launches.append(entry); return dict(exit=0)
            with contextlib.redirect_stdout(io.StringIO()):
                r.run_schedule(commands,output,result,lambda:None,lambda target:None,launch,
                               lambda i,e,p:[dict(valid=True)]*e['invocation']['observations'])
            self.assertEqual(result['measured_observations'],600)
            self.assertEqual(result['warmup_observations'],6)
            self.assertEqual(len(launches),66)
            self.assertEqual(result['unexecuted'],0)
            self.assertTrue(all(x['status']=='passed' for x in result['invocations']))
            self.assertTrue(all(e['argv'][-1]==str(output/'observations'/f'{i:03}.json') for i,e in enumerate(commands)))

    def test_private_recorder_bounds_preserve_pilot_defaults(self):
        from unittest.mock import Mock
        custom=dict(variant='A',fixture='3200x2400.png',observations=10)
        for bounds in (None,custom):
            with self.subTest(bounds=bounds),tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
                output=Path(temp); process=Mock(pid=999999)
                process.poll.return_value=None; process.wait.return_value=0
                def work(remaining):
                    self.assertGreater(remaining,0)
                    self.assertLessEqual(remaining,30)
                    return 'retained'
                header='# clockid: 1\n'+' '.join('sched:'+event for event in r.r.EVENTS)
                with patch.object(r.r.subprocess,'Popen',return_value=process),patch.object(r.r.os,'write'),patch.object(r.r.os,'read',return_value=b'ack\n'),patch.object(r.r.select,'select',return_value=([1],[],[])),patch.object(r.r,'command',return_value=header),patch.object(r.r.time,'monotonic',return_value=10):
                    value,metadata=r.r.capture(output,work,bounds=bounds)
                self.assertEqual(value,'retained')
                saved=v.read(output/'record-command.json')
                self.assertEqual(saved['bounds'],r.r.BOUNDS if bounds is None else custom)
                self.assertTrue(metadata['clock_verified'])
                process.send_signal.assert_called_once_with(r.r.signal.SIGINT)
                self.assertTrue(v.read(output/'recorder-shutdown.json')['reaped'])


spec=importlib.util.spec_from_file_location('validation_independent_tests',ROOT/'scripts/verify-preview-validation.py')
i=importlib.util.module_from_spec(spec); spec.loader.exec_module(i)


class IndependentVerificationTests(unittest.TestCase):
    setUp=ValidationPreparationTests.setUp

    def test_independent_interval_and_selection_arithmetic(self):
        row=measured_row('A','validation',1); row['validation']['scheduler']=None
        i.arithmetic(row)
        bad=copy.deepcopy(row); bad['validation']['parent_outside_nested'][0]['duration_ns']+=1
        with self.assertRaises(ValueError): i.arithmetic(bad)
        rows=[measured_row(variant,arm,index*100+j) for index,(variant,arm) in enumerate(v.COMBINATIONS) for j in range(100)]
        expected=i.selection_keys(rows)
        selected=a.selections(rows)
        self.assertEqual(expected,{(r['invocation_index'],r['observation']):r['selection_reasons'] for r in selected})
        self.assertEqual(i.distribution(range(1,101)),a.stats(list(range(1,101))))

    def test_independent_literal_reverse_reconstruction(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence,fixture,prepared=preparation_fixture(root)
            with patch.object(v.o.old,'FIXTURE_ROOT',fixture): result=v.prepare(evidence,root/'out')
            self.assertEqual(result['status'],'prepared')
            i.sources(root/'out')
            path=root/'out/validation/A/source/holonight-images/src/isolated/verification.cpp'
            path.write_text(path.read_text().replace('runtime file hash changed','modified error'))
            with self.assertRaises(ValueError): i.sources(root/'out')




class ValidationProvenanceRegressions(unittest.TestCase):
    setUp=ValidationPreparationTests.setUp

    def test_fixture_identity_resolves_through_bound_execution_registration(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); evidence,fixture,prepared=preparation_fixture(root)
            integrity=v.read(evidence/'integrity.json'); name=str(fixture/'3200x2400.png')
            digest=integrity['consumed'].pop(name)
            registration=root/'preregistration.json'
            v.write(registration,dict(prepared=str(prepared),fixture_identities={name:digest},fixtures={'3200x2400.png':digest}))
            integrity['consumed'][str(registration)]=v.o.digest(registration)
            v.write(evidence/'integrity.json',integrity); v.o.seal(evidence)
            with patch.object(v.o.old,'FIXTURE_ROOT',fixture): result=v.prepare(evidence,root/'out')
            self.assertEqual(result['status'],'prepared',result)
            self.assertEqual(v.read(root/'out/fixtures.json'),{name:digest})

    def test_validation_json_duplicate_keys_and_boolean_version_are_rejected(self):
        import json
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            target=Path(temp)/'sample.json'
            target.with_suffix('.stdout').write_text('')
            target.with_suffix('.stderr').write_text('VALIDATION {"version":1,"version":1}\n')
            with self.assertRaisesRegex(ValueError,'duplicate validation JSON'): a.records(target)
            events=validation_events(); events[0]['version']=True
            with self.assertRaises(ValueError): a.spans(events)
            target.with_suffix('.stderr').write_text('VALIDATION '+json.dumps(validation_events()[0])+'\n')
            self.assertEqual(a.records(target)[0]['line'],1)




class DesktopAnalysisRegressions(unittest.TestCase):
    setUp=ValidationPreparationTests.setUp

    def test_root_orchestration_and_analysis_are_rejected_before_creating_output(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            output=Path(temp)/'out'
            with patch.object(r.os,'geteuid',return_value=0):
                with self.assertRaisesRegex(ValueError,'must run without root'):
                    r.action(output,[],lambda result:self.fail('root work started'))
            self.assertFalse(output.exists())

    def test_privileged_recorder_only_records_and_forwards_desktop_reader_credentials(self):
        import os
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            output=Path(temp); data=output/'perf.data'; data.touch()
            request=output/'request.json'; v.write(request,dict(clock=dict(name='CLOCK_MONOTONIC',provenance='test-boot')))
            env=dict(PATH='/usr/bin',HOME='/tmp/desktop')
            credentials=dict(user=1000,group=1000,extra_groups=[1000])
            original=Path.stat
            def stat(path,*args,**kwargs):
                info=original(path,*args,**kwargs)
                if path==data:
                    values=list(info); values[4]=1000
                    return os.stat_result(values)
                return info
            with patch.object(r.os,'geteuid',return_value=0),patch.object(Path,'stat',stat),patch.object(r.r,'session',return_value=(env,credentials)),patch.object(r.r,'capture',return_value=(None,dict(clock_verified=True))) as capture,patch.object(r.r.n,'normalize',side_effect=AssertionError('root analysis forbidden')):
                r.recorder_worker(request,output)
            self.assertEqual(capture.call_args.kwargs['export_env'],env)
            self.assertEqual(capture.call_args.kwargs['export_credentials'],credentials)
            self.assertFalse((output/'scheduler.json').exists())
            self.assertFalse((output/'task-identities.json').exists())

    def test_normalization_requires_desktop_user_and_preserves_saved_export(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            output=Path(temp)
            with patch.object(r.os,'geteuid',return_value=0):
                with self.assertRaisesRegex(ValueError,'desktop user'): r.normalize_recording(output)
            raw=(ROOT/'tests/fixtures/preview-delivery-scheduler/perf-script.txt').read_text()
            (output/'perf-export.stdout').write_text(raw)
            metadata=dict(clock=dict(name='CLOCK_MONOTONIC',provenance='test-boot'),clock_verified=True,
                          boot_before='test-boot',boot_after='test-boot',start_ns=0,stop_ns=100)
            v.write(output/'recording-metadata.json',metadata)
            with patch.object(r.os,'geteuid',return_value=1000): r.normalize_recording(output)
            self.assertTrue(v.read(output/'scheduler.json')['export_complete'])
            self.assertEqual(v.read(output/'task-identities.json'),[])
            self.assertEqual((output/'perf-export.stdout').read_text(),raw)

    def test_loss_blocks_desktop_normalization_and_retains_evidence(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            output=Path(temp); raw='LOST 1 events\n'
            (output/'perf-export.stdout').write_text(raw)
            v.write(output/'recording-metadata.json',dict(clock=dict(name='CLOCK_MONOTONIC',provenance='test-boot'),
                clock_verified=True,boot_before='test-boot',boot_after='test-boot',start_ns=0,stop_ns=100))
            with patch.object(r.os,'geteuid',return_value=1000):
                with self.assertRaisesRegex(ValueError,'capture loss'): r.normalize_recording(output)
            self.assertEqual((output/'perf-export.stdout').read_text(),raw)
            self.assertEqual(v.read(output/'scheduler.json')['events'][0]['kind'],'loss')




def setup_validation_fixture():
    events=[]; next_span=0; ns=5
    def node(operation,children=(),parent=0,validation=0,ordinal=-1):
        nonlocal next_span,ns
        next_span+=1; token=next_span
        if operation in ('generation','runtime'): validation=token
        begin=dict(event(operation,token,parent,ns,validation=validation,ordinal=ordinal),observation=None)
        events.append(begin); ns+=1
        for child in children:
            if isinstance(child,str): node(child,parent=token,validation=validation,ordinal=ordinal)
            else: node(child[0],child[1],token,validation,child[2] if len(child)>2 else ordinal)
        events.append(dict(begin,ns=ns,edge='end',outcome='returned'));ns+=1
    runtime=('runtime',('initial_path_manifest',('manifest_parse',('manifest_read',)),
        'manifest_policy',('file',('record_prepare','attributes','file_open','read_hash','digest_compare'),0),'required_files','inventory'))
    node('generation',('protected_base','selector_descriptors','protected_generation',('nested_runtime',(runtime,)),
                       'generation_manifest_open_read','generation_manifest_parse_policy','generation_manifest_digest','generation_final_identity'))
    selected=a.spans(events); legacy=[]
    for span in selected:
        if span['operation'] not in ('generation','runtime'): continue
        begin={k:(span['begin'][k] or 0) for k in ('pid','tid','service','observation','job','worker','preparation')}
        begin.update(phase=span['operation']+'_validation',role='service_control',ns=span['start']-1,edge='begin')
        legacy.append(dict(cause='setup_activity',phase=begin['phase'],begin=begin,end=dict(begin,ns=span['stop']+1,edge='end'),
                           start=span['start']-1,stop=span['stop']+1))
    begin=dict(legacy[0]['begin'],phase='service_construction',tid=10,ns=0)
    legacy.append(dict(cause='setup_activity',phase='service_construction',begin=begin,end=dict(begin,ns=1,edge='end'),start=0,stop=1))
    observations=[dict(start_ns=1000,endpoints=dict(pixels=dict(delivery=dict(pid=10,service=99))))]
    mapping=[dict(ordinal=0,path='usr/a',size=100,sha256='a'*64)]
    return selected,dict(unassigned=legacy),mapping,observations


class SetupValidationRegressions(unittest.TestCase):
    setUp=ValidationPreparationTests.setUp

    def test_constructor_setup_retains_unavailable_observation_and_legacy_bindings(self):
        selected,lifecycle,mapping,observations=setup_validation_fixture()
        before=copy.deepcopy(selected)
        result=a.setup_validations(selected,lifecycle,mapping,'C',observations)
        self.assertEqual(len(result),1)
        self.assertIsNone(result[0]['observation'])
        self.assertEqual(result[0]['classification'],'v3_setup_activity')
        self.assertEqual(len(result[0]['bindings']),2)
        self.assertEqual(len(result[0]['validation']['files']),1)
        self.assertEqual(selected,before)
        self.assertEqual(observations,[dict(start_ns=1000,endpoints=dict(pixels=dict(delivery=dict(pid=10,service=99))))])

    def test_missing_ambiguous_foreign_and_overlapping_setup_is_rejected(self):
        for change in ('observation','measured_service','construction','binding','duplicate','overlap','pid','exception'):
            selected,lifecycle,mapping,observations=setup_validation_fixture()
            if change=='observation': selected[0]['begin']['observation']=1
            if change=='measured_service': observations[0]['endpoints']['pixels']['delivery']['service']=20
            if change=='construction': lifecycle['unassigned'].pop()
            if change=='binding': lifecycle['unassigned'][0]['begin']['tid']=99
            if change=='duplicate': lifecycle['unassigned'].append(copy.deepcopy(lifecycle['unassigned'][0]))
            if change=='overlap': observations[0]['start_ns']=1
            if change=='pid': observations[0]['endpoints']['pixels']['delivery']['pid']=99
            if change=='exception': selected[0]['end']['outcome']='exception'
            with self.subTest(change=change),self.assertRaises(ValueError):
                a.setup_validations(selected,lifecycle,mapping,'C',observations)


if __name__=='__main__': unittest.main()
