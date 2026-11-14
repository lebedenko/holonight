import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('gaps', Path(__file__).resolve().parents[1] / 'scripts/analyze-preview-delivery-overhead-gaps.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


class GapTests(unittest.TestCase):
    def report(self, count):
        report = dict(windows=[], spans=[], handoffs=[], events=[], unavailable=[])
        for observation in range(1, count+1):
            e = dict(pid=1, service=1, observation=observation, job=1, worker=1, generation=1,
                     preparation=None, session=1, transaction=1, publication=observation,
                     tid=1, ns=30, edge='point', operation='endpoint_pixels')
            report['handoffs'].append(dict(pid=1,publication=observation,identity=e))
            for endpoint in ('pixels','metadata'):
                report['windows'].append(dict(delivery=e,endpoint=endpoint,start_ns=10,stop_ns=30,
                                              boundary=dict(e,ns=10),categories={}))
        return report

    def test_full_schedule_local_identities_and_warmup_exclusion(self):
        rows=[]
        with patch('subprocess.Popen',side_effect=AssertionError('offline')), patch('os.system',side_effect=AssertionError('offline')):
            for i,s in enumerate(a.o.prep.schedule()):
                if s['mode']!='v4': continue
                current=a.endpoint_rows(self.report(s['observations']),s['variant'],s['fixture'],s['observations'])
                for r in current: r.update(invocation_index=i,block=s['block'],harness_latency_ns=30)
                if not s['warmup']: rows.extend(current)
        self.assertEqual(len(rows),2400)
        self.assertEqual(len({(r['invocation_index'],r['observation']) for r in rows}),1200)
        self.assertEqual(len(a.summaries(rows)),264)
        self.assertTrue(all(x['elapsed']['count']==100 for x in a.summaries(rows) if x['block']=='all'))
        self.assertEqual(a.selections(rows),a.selections(list(reversed(rows))))

    def test_count_validation(self):
        for count in (1,10):
            report=self.report(count)
            self.assertEqual(len(a.endpoint_rows(report,'A','f',count)),2*count)
            for bad in (report['windows'][:-1],report['windows'][:-1]+[report['windows'][0]]):
                broken=copy.deepcopy(report);broken['windows']=bad
                with self.assertRaises(ValueError): a.endpoint_rows(broken,'A','f',count)
        with self.assertRaises(ValueError): a.endpoint_rows({},'A','f',10)

    def test_distribution_and_clipping(self):
        self.assertEqual(a.distribution(range(1,101)),dict(count=100,minimum_ns=1,median_ns=50.5,p95_ns=95,maximum_ns=100))
        r=a.g.intervals(10,30,[dict(start=0,stop=20),dict(start=15,stop=40)])
        self.assertEqual(r['uncovered_ns'],0)
        self.assertEqual(r['covered_ns'],20)

    def test_ambiguous_boundaries_preserved(self):
        r=a.endpoint_rows(self.report(1),'A','f',1)[0]
        r['operations']=[dict(operation='op',begin=dict(r['boundary']),end=dict(r['delivery']))]
        gap=a.boundaries(r)[0]
        self.assertEqual(len(gap['left_records']),2)
        self.assertEqual(len(gap['right_records']),2)


if __name__=='__main__': unittest.main()

class OfflineFailureTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp=tempfile.TemporaryDirectory(dir=a.ROOT/'build')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ('prepared','prior','attempt/execution','attempt/native-build','attempt/report-privileged'):
            (self.root/name).mkdir(parents=True)
        for p in (self.root/'prepared',self.root/'prior',self.root/'attempt/execution',self.root/'attempt/native-build',self.root/'attempt/report-privileged'):
            a.o.seal(p)
        for name in ('subprocess.Popen','os.system','os.posix_spawn','os.fork'):
            guard=patch(name,side_effect=AssertionError('process launch forbidden'))
            guard.start(); self.addCleanup(guard.stop)

    def run_analysis(self):
        return a.analyze(self.root/'attempt',self.root/'prepared',self.root/'prior',self.root/'output')

    def test_bad_seal_retains_original_error_and_independent_checks(self):
        (self.root/'attempt/execution/new').write_text('drift')
        result=self.run_analysis()
        self.assertEqual(result['status'],'blocked')
        self.assertIn('integrity drift',result['failure'])
        checks=a.read(self.root/'output/integrity.json')['final_checks']
        self.assertFalse(checks[str(self.root/'attempt/execution')]['passed'])
        self.assertTrue(checks[str(self.root/'prior')]['passed'])
        a.o.check_output(self.root/'output')

    def test_input_drift_during_validation(self):
        def drift(_):
            (self.root/'prepared/drift').write_text('changed')
            raise ValueError('original validation failure')
        with patch.object(a.o,'verify',side_effect=drift): result=self.run_analysis()
        self.assertEqual(result['failure'],'original validation failure')
        self.assertFalse(a.read(self.root/'output/integrity.json')['final_checks'][str(self.root/'prepared')]['passed'])

    def test_destination_reuse_and_symlink_escape(self):
        (self.root/'output').mkdir()
        with self.assertRaises(ValueError): self.run_analysis()
        self.assertEqual(list((self.root/'output').iterdir()),[])

    def test_probe_hash_and_text_mismatch(self):
        base=self.root/'prepared/v4/A';base.mkdir(parents=True)
        source=base/'source.cpp';source.write_text('probe\n')
        p=dict(file=str(source),line=1,text='wrong',sha256=a.o.digest(source))
        a.write(base/'probe-to-source.json',dict(probes=[p]))
        with self.assertRaisesRegex(ValueError,'text mismatch'): a.g.validate_probes(self.root/'prepared/v4','A')
        p['text']='probe';p['sha256']='wrong'
        a.write(base/'probe-to-source.json',dict(probes=[p]))
        with self.assertRaisesRegex(ValueError,'hash mismatch'): a.g.validate_probes(self.root/'prepared/v4','A')
