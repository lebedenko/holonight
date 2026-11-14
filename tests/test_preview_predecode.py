import copy
import difflib
from contextlib import ExitStack
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('predecode', ROOT/'scripts/report-preview-predecode.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def part(spans, left=0, right=100):
    spans = [dict(operation=name, role='demand', start=start, stop=stop,
                  clipped_start=max(left,start), clipped_stop=min(right,stop)) for name,start,stop in spans]
    coverage = a.b.g.g.intervals(left,right,spans)
    return dict(start_ns=left, stop_ns=right, spans=spans, **coverage)


def endpoints():
    p=part([('helper_prepare',0,80),('runtime_validation',10,60)])
    row=dict(invocation_index=1, observation=1, variant='A', block=0, fixture='3200x2400.png',
             trace_origin={}, decode_boundary={}, delivery=dict(pid=1,service=2,observation=1,job=3,worker=4),
             harness_latency_ns=120,coarse=dict(pre_decode=p))
    return [dict(copy.deepcopy(row),endpoint=e) for e in ('pixels','metadata')]


def source_fixture(root, extra=''):
    origin=root/'origin'; prepared=root/'prepared'; qualification=root/'qualification'
    original=b'void work() {\n  run();\n}\n'
    traced=('#include "'+str(origin/'trace.h')+'"\nvoid work() {\n  StandbyTrace::Scope trace("runtime_validation", &root, -1);\n'+extra+'  run();\n}\n').encode()
    pairs={}
    for mode,data in (('AU',original),('AT',traced)):
        base=origin/mode
        (base/'source').mkdir(parents=True); (base/'harness-source').mkdir()
        (base/'source/work.cpp').write_bytes(data)
        (base/'harness-source/harness.cpp').write_text('harness\n')
        pairs[mode]={group:a.o.inventory(base/group) for group in ('source','harness-source')}
    diff=''.join(difflib.unified_diff(original.decode().splitlines(True),traced.decode().splitlines(True),
                fromfile=str(origin/'AU/source/work.cpp'),tofile=str(origin/'AT/source/work.cpp')))
    (origin/'A-tracing.diff').write_text(diff)
    a.write(origin/'preparation.json',dict(pairs=pairs,retained_unchanged=True,equivalence={'A':{'source':[]}}))
    a.o.seal(origin)
    prepared.mkdir(); qualification.mkdir()
    a.write(prepared/'manifest.json',dict(status='prepared',issues=[],inputs=dict(v3=str(origin))))
    before={str(origin/'seal.json'):a.o.digest(origin/'seal.json')}
    a.write(prepared/'input-integrity.json',dict(unchanged=True,before=before,after=before))
    for mode in ('v3','v4'):
        base=prepared/mode/'A'; (base/'source').mkdir(parents=True)
        (base/'source/work.cpp').write_bytes(traced)
        a.write(base/'source-inventory.json',dict(source=a.o.inventory(base/'source')))
    a.write(prepared/'anchor-review.json',{'A':[]})
    (qualification/'A/source').mkdir(parents=True)
    (qualification/'A/source/work.cpp').write_bytes(original)
    a.write(qualification/'freeze.json',dict(source_inventories={'A':a.o.inventory(qualification/'A/source')}))
    def consume(path,digest=None):
        a.require(digest is None or a.o.digest(path)==digest,'consumed hash mismatch')
        return a.read(path) if path.suffix=='.json' else path.read_text()
    return prepared,qualification,consume


class PredecodeTests(unittest.TestCase):
    def setUp(self):
        stack=ExitStack(); self.addCleanup(stack.close)
        for name in ('subprocess.Popen','subprocess.run','os.system','os.popen','os.fork','os.posix_spawn'):
            stack.enter_context(patch(name,side_effect=AssertionError('process launch forbidden')))

    def test_dual_endpoints_deduplicate_and_keep_latencies(self):
        rows=endpoints(); rows[1]['harness_latency_ns']=140
        rows[0]['coarse']['pre_decode']['share']=.6
        rows[1]['coarse']['pre_decode']['share']=.59
        result=a.observations(rows)
        self.assertEqual(len(result),1)
        self.assertEqual([r['harness_latency_ns'] for r in result[0]['endpoints'].values()],[120,140])
        self.assertEqual(len(a.observations(rows+[dict(r,invocation_index=2) for r in rows])),2)

    def test_mismatched_boundary_or_ownership_fails(self):
        for field,value in (('stop_ns',101),('start_ns',1)):
            rows=copy.deepcopy(endpoints()); rows[1]['coarse']['pre_decode'][field]=value
            with self.assertRaisesRegex(ValueError,'endpoint mismatch'): a.observations(rows)
        rows=copy.deepcopy(endpoints()); rows[1]['delivery']['job']=99
        with self.assertRaisesRegex(ValueError,'identity mismatch'): a.observations(rows)
        with self.assertRaisesRegex(ValueError,'endpoint'): a.observations(endpoints()[:1])
        with self.assertRaisesRegex(ValueError,'endpoint'): a.observations(endpoints()*2)

    def test_clipping_nesting_and_cross_thread_overlap_reconcile(self):
        p=part([('generation_validation',-10,60),('runtime_validation',10,50),('helper_prepare',40,110)])
        r=a.analyze(p,'C')
        self.assertEqual(sum(r['groups_ns'].values()),100)
        self.assertEqual(r['groups_ns']['generation_validation + helper_prepare + runtime_validation'],10)
        self.assertEqual(r['phases']['generation_validation']['union_ns'],60)
        self.assertEqual(r['phases']['helper_prepare']['inclusive_ns'],60)
        self.assertEqual(r['parent_outside_nested']['generation_validation']['duration_ns'],20)
        self.assertEqual(r['parent_outside_nested']['helper_prepare']['duration_ns'],50)

    def test_repeated_phase_spans_union_is_distinct_from_inclusive(self):
        r=a.analyze(part([('helper_prepare',0,70),('helper_prepare',30,90)]),'A')
        self.assertEqual(r['phases']['helper_prepare']['union_ns'],90)
        self.assertEqual(r['phases']['helper_prepare']['inclusive_ns'],130)
        self.assertEqual(r['groups_ns'],{'helper_prepare':90,'uncovered':10})

    def test_uncovered_and_missing_are_explicit(self):
        r=a.analyze(part([]),'A')
        self.assertEqual(r['groups_ns'],{'uncovered':100})
        self.assertEqual(r['largest_uncovered_ns'],100)
        self.assertIsNone(r['phases']['runtime_validation']['union_ns'])
        self.assertEqual(r['phases']['generation_validation']['availability'],'absent_by_design')
        self.assertIsNone(a.analyze(part([]),'C')['parent_outside_nested']['generation_validation']['duration_ns'])

    def test_invalid_coverage_or_role_fails(self):
        p=part([]); p['uncovered_ns']=0
        with self.assertRaisesRegex(ValueError,'reconciliation'): a.analyze(p,'C')
        p=part([('helper_prepare',0,50)]); p['spans'][0]['role']='standby'
        with self.assertRaisesRegex(ValueError,'foreign'): a.analyze(p,'C')

    def test_subtraction_is_per_observation_and_group_absence_is_zero(self):
        rs=[]
        for v in ('A','C'):
            for i,(parent,child) in enumerate(((80,10),(90,85),(50,20))):
                rs.append(dict(variant=v,block=0,**a.analyze(part([('helper_prepare',0,parent),('runtime_validation',0,child)]),v)))
        summary=a.summarize(rs)
        c=next(r for r in summary if r['variant']=='C' and r['block']=='pooled')
        self.assertEqual(c['parent_outside_nested']['helper_prepare']['median'],30)
        self.assertNotEqual(c['phases']['helper_prepare']['union_ns']['median']-c['phases']['runtime_validation']['union_ns']['median'],30)
        rs[0]=dict(variant='A',block=0,**a.analyze(part([]),'A'))
        a_summary=next(r for r in a.summarize(rs) if r['variant']=='A' and r['block']=='pooled')
        self.assertEqual(a_summary['groups']['helper_prepare + runtime_validation']['duration_ns']['minimum'],0)

    def test_rank_is_deterministic_with_p95_and_label_ties(self):
        groups={n:dict(share=dict(median=.3,p95=p)) for n,p in [('z',.4),('b',.5),('a',.5)]}
        summary=[dict(variant=v,block='pooled',groups=groups) for v in ('A','C')]
        self.assertEqual(a.ranking(summary)['order'],['a','b','z'])

    def test_tied_selections_and_harness_reasons_survive(self):
        rs=[dict(variant=v,invocation_index=k,observation=i,duration_ns=n,largest_uncovered_ns=7)
            for k,v in enumerate(('A','C')) for i,n in enumerate((1,2,3,3,3,4,5,6))]
        selected=a.selections(rs,[dict(invocation_index=0,observation=0,endpoint='pixels',selection_reasons=['slowest_five_with_ties'])])
        self.assertEqual(len(selected),16)
        self.assertEqual(sum('predecode_slowest_five_with_ties' in r['selection_reasons'] for r in selected),12)
        self.assertIn('pixels_harness_slowest_five_with_ties',selected[0]['selection_reasons'])
        self.assertEqual(sum('predecode_nearest_median' in r['selection_reasons'] for r in selected),6)

    def test_restricted_source_reconstruction_proves_private_edits(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            result=a.source_comparison(*source_fixture(Path(temp)))
            self.assertEqual(result['status'],'equivalent')
            self.assertTrue(result['uninstrumented_inventory_equal'])
            self.assertEqual(result['reconstruction_residual'],[])

    def test_unrecognized_source_edit_remains_unavailable(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            result=a.source_comparison(*source_fixture(Path(temp),'  changeBehavior();\n'))
            self.assertEqual(result['status'],'unavailable')
            self.assertIn('changeBehavior',result['reconstruction_residual'][0]['diff'])

    def test_qualification_source_difference_is_retained(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            prepared,qualification,consume=source_fixture(Path(temp))
            (qualification/'A/source/work.cpp').write_text('different();\n')
            a.write(qualification/'freeze.json',dict(source_inventories={'A':a.o.inventory(qualification/'A/source')}))
            result=a.source_comparison(prepared,qualification,consume)
            self.assertEqual(result['status'],'unavailable')
            self.assertIn('different();',result['differences'][0]['diff'])

    def test_destination_must_be_fresh_and_disjoint(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); startup=root/'startup'; qualification=root/'qualification'
            startup.mkdir(); qualification.mkdir()
            with self.assertRaisesRegex(ValueError,'fresh output'):
                a.report(startup,qualification,startup)
            with self.assertRaisesRegex(ValueError,'disjoint'):
                a.report(startup,qualification,startup/'new')

    def test_provenance_seal_mismatch_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            prepared,qualification,consume=source_fixture(Path(temp))
            (Path(temp)/'origin/seal.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'hash mismatch'):
                a.source_comparison(prepared,qualification,consume)

    def test_private_reconstruction_keeps_unrecognized_trace_and_production_statements(self):
        data=b'  StandbyTrace::arbitrary(run());\n  run();\n'
        self.assertEqual(a.reconstruct_v3(data),data)

    def test_quantiles(self):
        self.assertEqual(a.stats(range(1,11)),dict(count=10,minimum=1,median=5.5,p95=10,maximum=10))

    def test_integrity_failures_are_sealed_without_rankings(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); startup=root/'startup'; qualification=root/'qualification'
            startup.mkdir(); qualification.mkdir()
            a.write(startup/'assessment.json',dict(status='complete'))
            a.write(startup/'integrity.json',dict(passed=True,before={},consumed={}))
            a.o.seal(startup)
            result=a.report(startup,qualification,root/'output')
            self.assertEqual(result['status'],'blocked')
            self.assertIn('qualification provenance mismatch',result['failure'])
            a.o.check_output(root/'output')
            self.assertFalse((root/'output/rankings.json').exists())
            self.assertIn('not verified conclusions',(root/'output/REPORT.md').read_text())

    def test_input_drift_is_sealed(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as temp:
            root=Path(temp); startup=root/'startup'; qualification=root/'qualification'
            startup.mkdir(); qualification.mkdir()
            original=a.o.check_output
            def mutate(path):
                (qualification/'drift').write_text('changed')
                original(path)
            with patch.object(a.o,'check_output',side_effect=mutate):
                result=a.report(startup,qualification,root/'output')
            self.assertEqual(result['status'],'blocked')
            self.assertEqual(result['integrity_failure'],'input drift')
            original(root/'output')


if __name__=='__main__': unittest.main()
