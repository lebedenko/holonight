import copy
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scheduler',ROOT/'scripts/analyze-preview-delivery-scheduler.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)


class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack()
        for name in ('subprocess.Popen','subprocess.run','subprocess.call','subprocess.check_call',
                     'subprocess.check_output','os.system','os.popen','os.posix_spawn','os.posix_spawnp',
                     'os.fork','os.execv','os.execve','os.spawnv','os.spawnve'):
            self.stack.enter_context(patch(name,side_effect=AssertionError('process launch forbidden')))
        self.addCleanup(self.stack.close)

    def inputs(self,count=1):
        invocations=[]; records=[]
        for invocation in ('one','two'):
            report=dict(issues=[],handoffs=[],spans=[])
            for i in range(count):
                pub=i+1; t=10+i*100
                e=dict(pid=1,tid=2,publication=pub,ns=t+10)
                report['handoffs'].append(dict(identity=e))
                report['spans'] += [dict(operation='callback_execution',begin=e,start=t+10,stop=t+15,end=dict(e,ns=t+15)),
                    dict(operation='enqueue_call',begin=dict(e,ns=t-5,tid=3),end=dict(e,ns=t+20,tid=3),start=t-5,stop=t+20)]
                for edge,ns in (('enter',t),('publication',t+5),('exit',t+30)):
                    records.append(dict(version=1,invocation=invocation,pid=1,tid=2,dispatch=pub,parent=0,
                                        publication=pub if edge=='publication' else 0,edge=edge,ns=ns))
            invocations.append(dict(invocation=invocation,accounting=report,clock=dict(name='CLOCK_MONOTONIC',provenance='boot1')))
        return invocations,records

    def test_local_collisions_counts_and_callback_before_return(self):
        for count in (1,10):
            result=a.account(*self.inputs(count))
            self.assertEqual(len(result['rows']),count*2)
            self.assertTrue(all(r['link_status']=='linked' and r['callback_before_invoke_return'] for r in result['rows']))
            self.assertFalse(result['scheduler_available'])
            self.assertFalse(result['attribution_complete'])

    def test_missing_duplicate_malformed_and_nested(self):
        inv,rs=self.inputs()
        self.assertEqual(a.account(inv,rs+rs[1:2])['rows'][0]['link_status'],'ambiguous_or_missing')
        self.assertEqual(a.account(inv,[r for r in rs if r['edge']!='publication'])['rows'][0]['link_status'],'ambiguous_or_missing')
        with self.assertRaises(ValueError): a.account(inv,[dict(rs[0],ns=True)])
        nested=[dict(rs[0],dispatch=20,parent=1,ns=11),dict(rs[2],dispatch=20,parent=1,ns=25)]
        self.assertFalse(a.account(inv,rs+nested)['issues'])
        nested[1]['ns']=100
        self.assertTrue(a.account(inv,rs+nested)['issues'])

    def capture(self):
        return dict(version=1,clock=dict(name='CLOCK_MONOTONIC',provenance='boot1'),start_ns=0,stop_ns=100,
                    tasks=[dict(key=[1,2,1],start_ns=0,stop_ns=100,initial='running',cpu=0),
                           dict(key=[1,3,1],start_ns=0,stop_ns=100,initial='runnable')],events=[
            dict(kind='switch',ns=10,cpu=0,prev=[1,2,1],next=[1,3,1],prev_state='runnable'),
            dict(kind='wakeup',ns=20,cpu=1,task=[1,2,1]),
            dict(kind='switch',ns=30,cpu=0,prev=[1,3,1],next=[1,2,1],prev_state='non_runnable')])

    def test_preemption_wakeup_clipping_and_nonadditivity(self):
        c=self.capture(); timelines,issues=a.scheduler(c,c['clock'])
        self.assertFalse(issues)
        self.assertEqual(a.clipped(timelines[1,2,1],5,35)['totals'],dict(running=10,runnable=20,non_runnable=0,unknown=0))
        self.assertEqual(a.clipped(timelines[1,3,1],25,40)['totals']['non_runnable'],10)
        self.assertEqual(a.clipped([],0,100)['totals']['unknown'],100)
        # Each thread is a separate view; overlapping wall intervals are never summed.
        self.assertEqual(a.clipped(timelines[1,2,1],0,100)['totals']['running'],80)

    def test_clock_loss_unknown_reuse_and_truncation(self):
        c=self.capture()
        with self.assertRaises(ValueError): a.scheduler(c,dict(name='CLOCK_MONOTONIC',provenance='other'))
        c['tasks'][0]['initial']='unknown'
        t,_=a.scheduler(c,c['clock']); self.assertEqual(t[1,2,1][0]['state'],'unknown')
        c=self.capture(); c['events'].append(dict(kind='loss',ns=40,count=1))
        t,issues=a.scheduler(c,c['clock']); self.assertTrue(issues)
        self.assertEqual(a.clipped(t[1,2,1],40,100)['totals']['unknown'],60)
        c=self.capture(); c['tasks'].append(dict(c['tasks'][0],key=[1,2,2]))
        with self.assertRaises(ValueError): a.scheduler(c,c['clock'])
        c=self.capture(); c['stop_ns']=20
        with self.assertRaises(ValueError): a.scheduler(c,c['clock'])

    def test_migration_reuse_and_missing_wakeup(self):
        c=self.capture()
        c['tasks'].append(dict(key=[0,0,1],start_ns=0,stop_ns=100,initial='running',cpu=1))
        c['events'][-1]=dict(kind='switch',ns=30,cpu=1,prev=[0,0,1],next=[1,2,1],prev_state='runnable')
        timelines,issues=a.scheduler(c,c['clock'])
        self.assertFalse(issues)
        self.assertEqual(timelines[1,2,1][-1]['cpu'],1)
        c=self.capture(); c['tasks'][0]['stop_ns']=50
        c['tasks'].append(dict(key=[1,2,2],start_ns=50,stop_ns=100,initial='unknown'))
        timelines,issues=a.scheduler(c,c['clock'])
        self.assertIn((1,2,2),timelines)
        self.assertEqual(a.clipped(timelines[1,2,2],50,100)['totals']['unknown'],50)
        c=self.capture(); c['events'][0]['prev_state']='non_runnable'; c['events'].pop(1)
        _,issues=a.scheduler(c,c['clock']); self.assertTrue(issues)

    def test_capture_coverage_and_concurrent_publications(self):
        inv,rs=self.inputs(); c=self.capture()
        result=a.account(inv,rs,c)
        self.assertTrue(result['attribution_complete'])
        c['tasks'][0]['start_ns']=15
        c['events']=[]
        self.assertFalse(a.account(inv,rs,c)['attribution_complete'])
        inv,rs=self.inputs()
        report=inv[0]['accounting']
        second=copy.deepcopy(report['handoffs'][0]); second['identity']['publication']=2
        report['handoffs'].append(second)
        for span in list(report['spans']):
            span=copy.deepcopy(span); span['begin']['publication']=2; span['end']['publication']=2
            report['spans'].append(span)
        rs.append(dict(rs[1],publication=2))
        result=a.account(inv,rs)
        self.assertTrue(all(r['link_status']=='linked' for r in result['rows']))
        self.assertEqual(result['rows'][0]['dispatch'],result['rows'][1]['dispatch'])

    def test_offline_output_reuse_and_sealed_failure(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            base=Path(tmp); inv,rs=self.inputs()
            a.o.write(base/'v4.json',inv); a.o.write(base/'supp.json',rs)
            result=a.analyze(base/'v4.json',base/'supp.json',None,base/'ok')
            self.assertEqual(result['status'],'complete'); a.o.check_output(base/'ok')
            with self.assertRaises(ValueError): a.analyze(base/'v4.json',base/'supp.json',None,base/'ok')
            (base/'escape').symlink_to(base/'ok',target_is_directory=True)
            with self.assertRaises(ValueError): a.analyze(base/'v4.json',base/'supp.json',None,base/'escape'/'child')
            a.o.write(base/'supp.json',[{}])
            result=a.analyze(base/'v4.json',base/'supp.json',None,base/'bad')
            self.assertIn('failure',result); a.o.check_output(base/'bad')
            self.assertTrue(all(v['passed'] for v in a.o.read(base/'bad'/'integrity.json')['final_checks'].values()))


class PreparationTests(SchedulerTests):
    def fixture(self,base):
        prepared=base/'prepared'; prepared.mkdir()
        outputs={}
        for mode in ('v3','v4'):
            for variant in 'ABCD':
                root=prepared/mode/variant
                for group in a.o.prep.GROUPS: (root/group).mkdir(parents=True)
                (root/'trace.h').write_text('// frozen header\n')
                (root/'harness-source/main.cpp').write_text('QCoreApplication app(argc, argv);\n')
                (root/'source/test.cpp').write_text('#include "'+str(root/'trace.h')+'"\nDeliveryTrace::Scope delivery_callback("callback_execution");\n')
                a.o.write(root/'source-inventory.json',{g:a.o.inventory(root/g) for g in a.o.prep.GROUPS})
                a.o.write(root/'probe-to-source.json',dict(probes=a.o.prep.probes(root,mode=='v4')))
                outputs[mode+'/'+variant]=a.o.inventory(root)
        a.o.write(prepared/'manifest.json',dict(status='prepared',issues=[],outputs=outputs))
        a.o.write(prepared/'input-integrity.json',dict(unchanged=True,before={},after={},trees={}))
        a.o.write(prepared/'equivalence.json',{v:dict(exact_replay=True) for v in 'ABCD'})
        a.o.write(prepared/'protocol.json',dict(schedule=a.o.prep.schedule(),invocations=264,measured_observations=2400,warmups=24,timeout_seconds=120,termination_grace_seconds=5,retries=0))
        a.o.seal(prepared)
        gap=base/'gap'; gap.mkdir()
        a.o.write(gap/'assessment.json',dict(status='complete'))
        a.o.write(gap/'integrity.json',dict(before={str(prepared):a.o.inventory(prepared)},final_checks=dict(inputs=dict(passed=True))))
        a.o.write(gap/'independent-verification.json',dict(status='passed',checks=dict(replay=dict(passed=True))))
        a.o.seal(gap)
        return prepared,gap

    def test_preparation_replay_probes_and_source_mismatch(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            base=Path(tmp); prepared,gap=self.fixture(base)
            result=a.p.prepare(prepared,gap,base/'out')
            self.assertEqual(result['status'],'prepared')
            a.p.verify_generated(base/'out',prepared); a.o.check_output(base/'out')
            text=(base/'out/A/harness-source/main.cpp').read_text()
            self.assertIn('#include "',text)
            self.assertIn('SchedulerTrace::Application',text)
            with self.assertRaises(ValueError): a.p.prepare(prepared,gap,base/'out')
            (base/'out/A/source/test.cpp').write_text('drift')
            with self.assertRaises(ValueError): a.p.verify_generated(base/'out',prepared)
            (prepared/'v4/A/source/test.cpp').write_text('mismatch')
            result=a.p.prepare(prepared,gap,base/'blocked')
            self.assertEqual(result['status'],'blocked'); self.assertIn('failure',result)
            a.o.check_output(base/'blocked')
            self.assertTrue(all(c['passed'] for c in a.o.read(base/'blocked/integrity.json')['final_checks'].values()) is False)

    def test_input_drift_keeps_original_failure_and_independent_checks(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as tmp:
            base=Path(tmp); prepared,gap=self.fixture(base)
            def drift(*args):
                (prepared/'changed').write_text('drift')
                raise ValueError('original failure')
            with patch.object(a.p,'verify_generated',side_effect=drift):
                result=a.p.prepare(prepared,gap,base/'out')
            self.assertEqual(result['failure'],'original failure')
            checks=a.o.read(base/'out/integrity.json')['final_checks']
            self.assertFalse(checks[str(prepared)]['passed']); self.assertTrue(checks[str(gap)]['passed'])
            a.o.check_output(base/'out')


if __name__=='__main__': unittest.main()
