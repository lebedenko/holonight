import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cold',ROOT/'scripts/assess-preview-cold-start.py')
a=importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def endpoints():
    spans=[dict(operation='runtime_validation',role='demand',start=10,stop=50,clipped_start=10,clipped_stop=50)]
    part=dict(start_ns=0,stop_ns=60,spans=spans,**a.b.g.g.intervals(0,60,spans))
    identity=dict(pid=1,service=2,observation=1,job=3,worker=4,ns=100)
    row=dict(invocation_index=1,observation=1,variant='A',block=0,fixture='3200x2400.png',
             trace_origin=dict(ns=0),decode_boundary={},delivery=identity,harness_latency_ns=100,
             unavailable=[],coarse=dict(pre_decode=part),v3_timeline=[],operations=[])
    return [dict(copy.deepcopy(row),endpoint=e) for e in ('pixels','metadata')]


class ColdStartTests(unittest.TestCase):
    def test_identity_mismatch_blocks_comparison(self):
        rs=endpoints(); rs[1]['delivery']['worker']=99
        with self.assertRaisesRegex(ValueError,'identity mismatch'): a.rows(rs)

    def test_population_separation(self):
        for field,value in [('warmup',True),('mode','v3'),('fixture','160x80.png')]:
            rs=endpoints()
            for r in rs:r[field]=value
            with self.assertRaisesRegex(ValueError,'foreign population'): a.rows(rs)
        rs=a.rows(endpoints())
        other=[dict(r,population='separate-validation') for r in rs]
        self.assertEqual(len(a.summarize(rs+other)),4)

    def test_nested_and_overlapping_intervals_are_not_added(self):
        rs=endpoints()
        for r in rs:
            r['operations']=[dict(operation=n,start=x,stop=y) for n,x,y in
                [('store_raster',40,90),('png_serialization',50,80),('storage_commit',70,95)]]
        block=a.rows(rs)[0]['blocks']['thumbnail_storage']
        self.assertEqual(block['covered_ns'],55)
        self.assertEqual(block['inclusive_ns'],105)
        self.assertEqual(block['uncovered'],[[0,40],[95,100]])

    def test_missing_boundaries_remain_unavailable(self):
        rs=a.rows(endpoints()); block=rs[0]['blocks']['result_delivery']
        self.assertEqual(block['availability'],'unavailable; not zero')
        self.assertIsNone(a.summarize(rs)[0]['blocks']['result_delivery']['union_ns'])
        with self.assertRaisesRegex(ValueError,'endpoint'):a.rows(endpoints()[:1])

    def test_deterministic_ranking(self):
        summary=a.summarize(a.rows(endpoints()))
        self.assertEqual(a.ranking(summary),sorted(a.BLOCKS))
        summary[0]['variant']='C'
        summary[0]['blocks']['helper_preparation']['union_ns']=dict(median=5)
        self.assertEqual(a.ranking(list(reversed(summary)))[0],'helper_preparation')

    def test_missing_evidence_retains_sealed_blocked_result(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); inputs=[]
            for i in range(5):
                path=root/str(i);path.mkdir();inputs.append(path)
            out=root/'out'
            with patch('subprocess.Popen',side_effect=AssertionError('no launches')):
                result=a.run(*inputs,*[root/'missing']*3,out)
            self.assertEqual(result['status'],'blocked')
            self.assertIsNone(result['outcome'])
            a.o.check_output(out)
            self.assertTrue((out/'REPORT.md').exists())

    def test_consumed_drift_blocks_and_is_sealed(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); inputs=[]
            for i in range(5):
                path=root/str(i);path.mkdir();inputs.append(path)
            # A malformed sealed input is still consumed and must be rehashed.
            a.write(inputs[1]/'seal.json',{})
            digest=a.o.digest
            calls={}
            def drifting(path):
                key=str(path);calls[key]=calls.get(key,0)+1
                value=digest(path)
                return 'changed' if path==inputs[1]/'seal.json' and calls[key]>1 else value
            with patch.object(a.o,'digest',side_effect=drifting):
                result=a.run(*inputs,*[root/'missing']*3,root/'out')
            self.assertEqual(result['status'],'blocked')
            self.assertIn('integrity_failure',result)
            a.o.check_output(root/'out')


if __name__=='__main__':unittest.main()
