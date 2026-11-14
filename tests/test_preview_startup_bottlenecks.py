import copy
from contextlib import ExitStack
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('bottlenecks',ROOT/'scripts/report-preview-startup-bottlenecks.py')
a=importlib.util.module_from_spec(spec); spec.loader.exec_module(a)


class StartupTests(unittest.TestCase):
    def setUp(self):
        stack=ExitStack(); self.addCleanup(stack.close)
        for name in ('subprocess.Popen','subprocess.run','os.system','os.popen','os.fork','os.posix_spawn'):
            stack.enter_context(patch(name,side_effect=AssertionError('process launch forbidden')))
        e=dict(pid=1,service=2,observation=1,job=3,worker=4,generation=5,publication=6,ns=100)
        span=dict(phase='decode_exchange_including_transport',role='demand',start=30,stop=70,begin=e,end=e)
        self.life=dict(boundaries=dict(startup_origin=[dict(e,ns=0)]),timeline=[span])
        self.row=dict(delivery=e,start_ns=70,operations=[])

    def test_partition_clips_nested_spans_and_retains_uncovered(self):
        self.row['operations']=[dict(operation='store_raster',start=60,stop=90),dict(operation='png_serialization',start=75,stop=85)]
        r=a.partition(self.row,self.life)
        self.assertEqual([r['coarse'][n]['duration_ns'] for n in a.NAMES],[30,40,30])
        post=r['coarse']['post_decode']
        self.assertEqual(post['covered_ns'],20)
        self.assertEqual(post['overlapping_span_excess_ns'],10)
        self.assertEqual(post['uncovered'],[[90,100]])

    def test_missing_and_ambiguous_boundaries_fail(self):
        for count in (0,2):
            life=copy.deepcopy(self.life); life['timeline']*=count
            with self.assertRaisesRegex(ValueError,'decode'): a.partition(self.row,life)
            life=copy.deepcopy(self.life); life['boundaries']['startup_origin']*=count
            with self.assertRaisesRegex(ValueError,'origin'): a.partition(self.row,life)

    def test_foreign_observation_does_not_supply_boundary(self):
        self.life['timeline'][0]['begin']=dict(self.row['delivery'],observation=2)
        with self.assertRaisesRegex(ValueError,'decode'): a.partition(self.row,self.life)

    def test_quantiles_are_nearest_rank(self):
        self.assertEqual(a.stats(list(range(1,11))),dict(count=10,minimum=1,median=5.5,p95=10,maximum=10))
        self.assertEqual(a.stats(list(range(1,101)))['p95'],95)

    def test_dual_endpoints_count_publication_once_and_invocations_separately(self):
        rows=[dict(invocation_index=i,observation=1,delivery=dict(pid=1,publication=2)) for i in (1,1,2,2)]
        self.assertEqual(a.denominators(rows),dict(observations=2,endpoints=4,publications=2))

    def test_selection_retains_all_cutoff_median_and_gap_ties(self):
        rows=[dict(variant=v,endpoint=e,harness_latency_ns=n,largest_uncovered_ns=7) for v in ('A','C') for e in ('pixels','metadata') for n in (1,2,3,3,3,4,5,6)]
        selected=a.selections(rows)
        tails=[r for r in selected if 'slowest_five_with_ties' in r['selection_reasons']]
        self.assertEqual(len(tails),24)
        self.assertEqual(len(selected),32)

    def test_ranking_uses_share_p95_then_name(self):
        summary=[dict(variant=v,endpoint=e,block='pooled',intervals={n:dict(share=dict(median=.3,p95=.4)) for n in a.NAMES}) for v in ('A','C') for e in ('pixels','metadata')]
        self.assertEqual(a.rankings(summary)[0]['order'],sorted(a.NAMES))
        summary[2]['intervals']['post_decode']['share']['p95']=.5
        self.assertEqual(a.rankings(summary)[0]['order'][0],'post_decode')

    def test_failure_is_sealed_and_cannot_present_rankings(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); inputs=[]
            for name in ('delivery','scheduler','qualification'):
                p=root/name; p.mkdir(); inputs.append(p)
            output=root/'result'
            result=a.report(*inputs,output)
            self.assertEqual(result['status'],'blocked')
            a.o.check_output(output)
            self.assertFalse((output/'rankings.json').exists())
            self.assertIn('Partial rankings are not verified',(output/'REPORT.md').read_text())


    def test_input_drift_is_sealed_as_integrity_failure(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); inputs=[]
            for name in ('delivery','scheduler','qualification'):
                path=root/name; path.mkdir(); inputs.append(path)
            original=a.o.inventory
            calls={}
            def drift(path):
                key=str(path); calls[key]=calls.get(key,0)+1
                return original(path) if calls[key]==1 else {'drift':'changed'}
            with patch.object(a.o,'inventory',side_effect=drift):
                result=a.report(*inputs,root/'output')
            self.assertEqual(result['status'],'blocked')
            self.assertEqual(result['integrity_failure'],'input drift')
            a.o.check_output(root/'output')

    def test_signed_publication_window_preserves_negative_ordering(self):
        e=dict(pid=10,tid=11,service=1,observation=1,job=2,worker=3,
               preparation=None,generation=4,session=5,transaction=6,
               publication=7,endpoint='final_result',ns=40)
        endpoint=dict(endpoint='metadata',record=dict(e,operation='endpoint_metadata'))
        report=dict(issues=[],assessment_available=True,
                    spans=[dict(operation=op,begin=dict(e,ns=start),end=dict(e,ns=stop),start=start,stop=stop)
                           for op,start,stop in [('enqueue_call',10,35),('callback_execution',30,50)]],
                    windows=[dict(delivery=endpoint['record'],endpoint='metadata')],
                    handoffs=[dict(identity=e,endpoints=[endpoint])])
        self.assertEqual(a.s.publication_rows(report,'local')[0]['invoke_return_to_callback_ns'],-5)


if __name__=='__main__': unittest.main()
