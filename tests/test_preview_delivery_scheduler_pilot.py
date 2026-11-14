import copy
import difflib
import importlib.util
from pathlib import Path
import tempfile
from unittest.mock import patch, Mock
import unittest
import test_preview_delivery_scheduler as base
a=base.a

ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result
n=module('normalizer_tests','normalize-preview-delivery-perf.py')
r=module('runner_tests','run-preview-delivery-scheduler.py')


class OfflineMixin:
    setUp=base.SchedulerTests.setUp
    inputs=base.SchedulerTests.inputs
    capture=base.SchedulerTests.capture
    fixture=base.PreparationTests.fixture


class DispatchRegressions(OfflineMixin,unittest.TestCase):
    def test_parent_publication_during_child_rejected(self):
        inv,records=self.inputs()
        child=[dict(records[0],dispatch=8,parent=1,ns=11),dict(records[2],dispatch=8,parent=1,ns=25)]
        result=a.account(inv,sorted(records+child,key=lambda row:(row['invocation'],row['ns'])))
        self.assertTrue(result['issues'])
        self.assertEqual(result['rows'][0]['link_status'],'ambiguous_or_missing')

    def test_sibling_overlap_orphan_and_conflicting_records(self):
        inv,records=self.inputs()
        for bad in ([dict(records[1],publication=99)], [dict(records[0],dispatch=2,ns=12),dict(records[2],dispatch=2,ns=35)], [dict(records[0],tid=9),dict(records[2],tid=9)]):
            with self.subTest(bad=bad):
                self.assertTrue(a.account(inv,sorted(records+bad,key=lambda row:(row['invocation'],row['ns'])))['issues'])

    def test_missing_unrelated_history_is_scoped(self):
        inv,records=self.inputs(); capture=self.capture()
        capture['tasks'] += [dict(key=[9,9,1],start_ns=0,stop_ns=100,initial='unknown'),dict(key=[9,10,1],start_ns=0,stop_ns=100,initial='unknown')]
        capture['events'].append(dict(kind='switch',ns=40,cpu=5,prev=[9,9,1],next=[9,10,1],prev_state='non_runnable'))
        result=a.account(inv,records,capture)
        self.assertTrue(result['scheduler_issues'])
        self.assertTrue(result['attribution_complete'])
        capture['events'][0]['prev_state']='non_runnable'; capture['events'].pop(1)
        self.assertFalse(a.account(inv,records,capture)['attribution_complete'])

    def test_positive_return_window_is_split_on_both_threads(self):
        inv,records=self.inputs()
        for v in inv:
            s=v['accounting']['spans'][1]; s['stop']=8; s['end']['ns']=8
        result=a.account(inv,records,self.capture())
        for row in result['rows']:
            self.assertEqual(row['invoke_return_to_dispatch_ns'],2)
            for thread in row['thread_accounting']:
                self.assertEqual(sum(thread['parts']['return_to_dispatch']['totals'].values()),2)
                self.assertEqual(sum(thread['parts']['dispatch_to_callback']['totals'].values()),10)
                self.assertEqual(sum(thread['totals'].values()),12)


class PreparationRegressions(OfflineMixin,unittest.TestCase):
    def test_self_consistent_unauthorized_patch_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            base=Path(tmp); prepared,gap=self.fixture(base); out=base/'out'
            self.assertEqual(a.p.prepare(prepared,gap,out)['status'],'prepared')
            path=out/'A/source/test.cpp'; path.write_text(path.read_text()+'// unauthorized\n')
            anchors=a.o.read(out/'anchors.json')
            for anchor in anchors:
                if anchor['file']=='A/source/test.cpp': anchor['after']=path.read_text()
            a.o.write(out/'anchors.json',anchors)
            for i,anchor in enumerate(anchors,1):
                relative=Path(anchor['file'])
                patch=''.join(difflib.unified_diff(anchor['before'].splitlines(True),anchor['after'].splitlines(True),fromfile=str(prepared/'v4'/relative),tofile=str(out/relative)))
                (out/(relative.parts[0]+'-'+str(i)+'.diff')).write_text(patch)
            a.o.seal(out)
            with self.assertRaisesRegex(ValueError,'unauthorized'): a.p.verify_generated(out,prepared)

    def test_removed_substitution_or_citation_is_rejected(self):
        for remove in ('substitution','citation'):
            with self.subTest(remove=remove),tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
                base=Path(tmp); prepared,gap=self.fixture(base); out=base/'out'
                a.p.prepare(prepared,gap,out)
                if remove=='substitution':
                    path=out/'A/harness-source/main.cpp'; path.write_text('QCoreApplication app(argc, argv);\n')
                else: a.o.write(out/'source-citations.json',[])
                with self.assertRaises(ValueError): a.p.verify_generated(out,prepared)

    def test_dispatch_sequence_is_independent(self):
        self.assertIn('id=sequence.fetch_add(1)',a.p.HEADER)
        self.assertNotIn('DeliveryTrace::identity()',a.p.HEADER)


class NormalizerTests(OfflineMixin,unittest.TestCase):
    def metadata(self):
        return dict(clock=dict(name='CLOCK_MONOTONIC',provenance='boot1'),clock_verified=True,boot_before='boot1',boot_after='boot1',start_ns=0,stop_ns=100)

    def test_saved_export_external_wakeup_idle_migration_reuse_and_references(self):
        path=ROOT/'tests/fixtures/preview-delivery-scheduler/perf-script.txt'
        capture=n.normalize(path.read_text(),self.metadata(),[dict(pid=10,tid=11,ns=35)],str(path))
        self.assertTrue(capture['export_complete']); self.assertFalse(capture['diagnostics'])
        timelines,issues=a.scheduler(capture,capture['clock'])
        self.assertIn((10,11,1),timelines); self.assertIn((None,11,2),timelines)
        self.assertIn((0,0,0),timelines); self.assertIn((0,0,1),timelines)
        self.assertEqual(a.clipped(timelines[10,11,1],30,40)['totals']['running'],10)
        self.assertEqual(capture['events'][1]['cpu'],1)
        self.assertEqual(capture['raw_records'][0]['file'],str(path))
        self.assertEqual(capture['events'][0]['raw']['line'],1)
        self.assertEqual(timelines[10,11,1][0]['state'],'unknown')

    def test_unknown_prefix_identity_preserves_final_switch_and_payload_tasks(self):
        for prefix in ('99/-1','-1/-1','-1/99'):
            with self.subTest(prefix=prefix):
                text=('worker 99/11 [000] 0.000000010: sched:sched_process_exit: comm=worker pid=11 prio=120\n'
                      ':-1 '+prefix+' [000] 0.000000020: sched:sched_switch: prev_comm=worker prev_pid=11 prev_state=X ==> next_comm=idle next_pid=0\n')
                with patch.object(n.a.o.subprocess,'Popen',side_effect=AssertionError('offline only')):
                    capture=n.normalize(text,self.metadata())
                self.assertTrue(capture['export_complete'])
                self.assertFalse(capture['diagnostics'])
                self.assertEqual(capture['events'][0]['prev'],[None,11,1])
                self.assertEqual(capture['events'][0]['next'],[0,0,0])
                task=next(t for t in capture['tasks'] if t['key']==[None,11,1])
                self.assertEqual(task['stop_ns'],20)
                self.assertEqual(capture['events'][0]['raw']['line'],2)

    def test_other_negative_or_malformed_prefix_remains_incomplete(self):
        for prefix in ('99/-2','-2/99','99/nope'):
            text='worker '+prefix+' [000] 0.000000020: sched:sched_switch: prev_pid=11 prev_state=X next_pid=0\n'
            self.assertFalse(n.normalize(text,self.metadata())['export_complete'])

    def test_clock_truncation_malformed_and_loss(self):
        text=(ROOT/'tests/fixtures/preview-delivery-scheduler/perf-script.txt').read_text()
        for change in (dict(clock_verified=False),dict(boot_after='other'),dict(stop_ns=50)):
            with self.subTest(change=change),self.assertRaises(ValueError): n.normalize(text,dict(self.metadata(),**change))
        c=n.normalize(text+'LOST 23 events\n',self.metadata())
        self.assertTrue(any(e['kind']=='loss' for e in c['events']))
        c=n.normalize('unparseable\n',self.metadata())
        self.assertFalse(c['export_complete'])

    def test_sealed_normalizer_output_and_reuse(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            base=Path(tmp)
            (base/'perf.txt').write_text((ROOT/'tests/fixtures/preview-delivery-scheduler/perf-script.txt').read_text())
            a.o.write(base/'metadata.json',self.metadata()); a.o.write(base/'identities.json',[])
            self.assertEqual(n.convert(base/'perf.txt',base/'metadata.json',base/'identities.json',base/'out')['status'],'complete')
            a.o.check_output(base/'out')
            with self.assertRaises(ValueError): n.convert(base/'perf.txt',base/'metadata.json',base/'identities.json',base/'out')


class RunnerTests(OfflineMixin,unittest.TestCase):
    def test_recording_configuration_and_fixed_limits(self):
        argv=r.record_argv(Path('/tmp/perf.data'))
        self.assertIn('--all-cpus',argv); self.assertNotIn('-g',argv)
        self.assertEqual(argv[argv.index('--mmap-pages')+1],'256')
        self.assertEqual(argv[argv.index('--clockid')+1],'CLOCK_MONOTONIC')
        self.assertEqual(sum(x=='-e' for x in argv),6)
        self.assertEqual(r.BOUNDS['observations'],[1,10]); self.assertEqual(r.BOUNDS['timeout_seconds'],30)
        self.assertEqual(r.BOUNDS['retries'],0)
        for header in ('# clockid: 1 (CLOCK_MONOTONIC)','# clockid: CLOCK_MONOTONIC'):
            r.clock_header(header)
        with self.assertRaises(ValueError): r.clock_header('# timestamps appear similar')
        with self.assertRaises(ValueError): r.clock_header('# clockid=1\n# clockid=0')

    def test_sealed_partial_failure_keeps_first_error_and_independent_checks(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            base=Path(tmp); consumed=base/'input'; consumed.mkdir(); (consumed/'value').write_text('old')
            def fail(result):
                (base/'out/partial').write_text('retained')
                (consumed/'value').write_text('drift')
                raise ValueError('original failure')
            with patch.object(r.o.gate,'scope_snapshot',return_value=dict(isolated=True)):
                result=r.sealed_action(base/'out',[consumed],fail)
            self.assertEqual(result['failure'],'original failure')
            a.o.check_output(base/'out')
            checks=a.o.read(base/'out/integrity.json')['final_checks']
            self.assertFalse(checks[str(consumed)]['passed']); self.assertTrue(checks['tools']['passed'])
            self.assertTrue((base/'out/partial').exists())
            with self.assertRaises(ValueError): r.sealed_action(base/'out',[consumed],fail)
            (base/'escape').symlink_to(base/'out',target_is_directory=True)
            with self.assertRaises(ValueError): r.sealed_action(base/'escape/child',[consumed],fail)

    def recorder(self):
        recorder=Mock(pid=999999)
        recorder.poll.return_value=None
        recorder.wait.return_value=0
        return recorder

    def test_capture_readiness_precedes_work_and_finalization(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            output=Path(tmp); recorder=self.recorder(); order=[]
            recorder.send_signal.side_effect=lambda sig:order.append('stop')
            recorder.wait.side_effect=lambda **kw:order.append('finalize') or 0
            recorder.poll.side_effect=lambda: None if 'finalize' not in order else 0
            def work(remaining):
                self.assertGreater(remaining,0); self.assertLessEqual(remaining,30)
                order.append('work'); return 'observations'
            def ack(fd,size): order.append('ready'); return b'ack\n'
            with patch.object(r.subprocess,'Popen',return_value=recorder),patch.object(r.os,'write'),patch.object(r.os,'read',side_effect=ack),patch.object(r.select,'select',return_value=([1],[],[])),patch.object(r,'command',return_value='# clockid: 1\n'+' '.join('sched:'+event for event in r.EVENTS)):
                value,metadata=r.capture(output,work)
            self.assertEqual(value,'observations')
            self.assertEqual(order,['ready','work','stop','finalize'])
            self.assertTrue(metadata['clock_verified'])
            self.assertTrue((output/'record-command.json').exists())

    def test_nul_terminated_or_fragmented_perf_acknowledgement(self):
        for chunks in ((b'ack\n\0',),(b'a',b'ck\n\0'),(b'ack\n',)):
            with self.subTest(chunks=chunks),tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
                recorder=self.recorder()
                with patch.object(r.select,'select',return_value=([1],[],[])),patch.object(r.os,'read',side_effect=chunks):
                    r.acknowledge(1,recorder,Path(tmp))
                self.assertEqual(a.o.read(Path(tmp)/'recorder-ack.json')['hex'],b''.join(chunks).hex())
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            with patch.object(r.select,'select',return_value=([1],[],[])),patch.object(r.os,'read',return_value=b'wrong'):
                with self.assertRaises(ValueError): r.acknowledge(1,self.recorder(),Path(tmp))

    def test_capture_readiness_timeout_prevents_work_and_retains_partial(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            output=Path(tmp); recorder=self.recorder(); work=Mock()
            with patch.object(r.subprocess,'Popen',return_value=recorder),patch.object(r.os,'write'),patch.object(r.select,'select',return_value=([],[],[])),patch.object(r.os,'killpg') as kill:
                with self.assertRaisesRegex(ValueError,'readiness timeout'): r.capture(output,work)
            work.assert_not_called(); recorder.send_signal.assert_called_once_with(r.signal.SIGINT)
            self.assertTrue(a.o.read(output/'recorder-shutdown.json')['reaped'])
            self.assertTrue((output/'recording-partial.json').exists())

    def test_failed_workload_is_not_retried_and_cleanup_keeps_first_error(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            output=Path(tmp); recorder=self.recorder()
            work=Mock(side_effect=ValueError('workload failed'))
            recorder.wait.side_effect=r.subprocess.TimeoutExpired('perf',5)
            with patch.object(r.subprocess,'Popen',return_value=recorder),patch.object(r.os,'write'),patch.object(r.os,'read',return_value=b'ack\n'),patch.object(r.select,'select',return_value=([1],[],[])),patch.object(r.os,'killpg'):
                with self.assertRaisesRegex(ValueError,'workload failed'): r.capture(output,work)
            work.assert_called_once()
            self.assertFalse(a.o.read(output/'recording-partial.json')['cleanup']['passed'])

    def test_eof_malformed_and_early_exit_prevent_acknowledgement(self):
        for chunk,exit_code in ((b'',None),(b'bad\n',None),(b'ack\n',1)):
            with self.subTest(chunk=chunk,exit=exit_code),tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
                recorder=self.recorder(); recorder.poll.return_value=exit_code
                with patch.object(r.select,'select',return_value=([1],[],[])),patch.object(r.os,'read',return_value=chunk):
                    with self.assertRaises(ValueError): r.acknowledge(1,recorder,Path(tmp))
                self.assertTrue((Path(tmp)/'recorder-ack.json').exists())

    def test_forced_shutdown_reaps_with_remaining_shared_deadline(self):
        recorder=self.recorder()
        recorder.wait.side_effect=[r.subprocess.TimeoutExpired('perf',4),-9]
        with patch.object(r.time,'monotonic',side_effect=[10,10,14,14.5]),patch.object(r.os,'killpg') as kill:
            result=r.shutdown(recorder)
        self.assertFalse(result['passed']); self.assertTrue(result['reaped'])
        self.assertTrue(result['timed_out']); self.assertTrue(result['forced'])
        self.assertEqual([call.kwargs['timeout'] for call in recorder.wait.call_args_list],[4,1])
        kill.assert_called_once_with(recorder.pid,r.signal.SIGKILL)

    def test_graceful_shutdown_reaps_and_accepts_only_success(self):
        for code in (0,1):
            recorder=self.recorder(); recorder.wait.return_value=code
            result=r.shutdown(recorder)
            self.assertTrue(result['reaped']); self.assertFalse(result['forced'])
            self.assertEqual(result['passed'],code==0)

    def test_sigint_exit_requires_readiness_and_our_shutdown_signal(self):
        for ready in (False,True):
            for already_exited in (False,True):
                with self.subTest(ready=ready,already_exited=already_exited):
                    recorder=self.recorder()
                    recorder.poll.return_value=-r.signal.SIGINT if already_exited else None
                    recorder.wait.return_value=-r.signal.SIGINT
                    result=r.shutdown(recorder,ready=ready)
                    self.assertEqual(result['passed'],ready and not already_exited)
                    self.assertTrue(result['reaped'])
                    self.assertEqual(result['sigint_sent'],not already_exited)
        recorder=self.recorder(); recorder.wait.return_value=-r.signal.SIGTERM
        self.assertFalse(r.shutdown(recorder,ready=True)['passed'])

    def test_blocked_preflight_cannot_build_or_execute(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            base=Path(tmp); package=base/'package'; package.mkdir(); preflight=base/'preflight'; preflight.mkdir()
            a.o.write(preflight/'assessment.json',dict(status='blocked')); a.o.seal(preflight)
            with patch.object(r.o.gate,'scope_snapshot',return_value=dict(isolated=True)):
                result=r.build(package,preflight,base/'build')
            self.assertEqual(result['status'],'blocked'); self.assertEqual(result['failure'],'preflight blocked')
            self.assertFalse((base/'build/B').exists()); a.o.check_output(base/'build')


if __name__=='__main__': unittest.main()
