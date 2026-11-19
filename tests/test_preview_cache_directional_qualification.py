"""Process-forbidden qualification, prerequisite and startup gate regressions."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

DIRECTORY=Path(__file__).resolve().parents[1]/'tooling/preview-cache-complexity-encoding-trial/qualification'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

previous={key:sys.modules.get(key) for key in ('contract','correctness','stage','qualify')}
sys.path.insert(0,str(DIRECTORY))
t=load('directional_qualification_contract',DIRECTORY/'contract.py')
sys.modules['contract']=t
c=load('directional_qualification_correctness',DIRECTORY/'correctness.py')
sys.modules['correctness']=c
stage=load('directional_qualification_stage',DIRECTORY/'stage.py')
sys.modules['stage']=stage
q=load('directional_qualification_controller',DIRECTORY/'qualify.py')
sys.modules['qualify']=q
r=load('directional_qualification_preparer',DIRECTORY/'run.py')
v=load('directional_qualification_verifier',DIRECTORY/'offline/verify.py')
vx=load('directional_qualification_execution_verifier',DIRECTORY/'offline/verify_execution.py')
x=load('directional_qualification_execution',DIRECTORY/'execute.py')
sys.path.remove(str(DIRECTORY))
for key,value in previous.items():
    if value is None: sys.modules.pop(key,None)
    else: sys.modules[key]=value


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess,'Popen',side_effect=AssertionError('process forbidden')))
        self.enterContext(patch.object(subprocess,'run',side_effect=AssertionError('process forbidden')))

    def test_missing_eligibility_prevents_prepare_and_attempt_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)/'prepared'
            with patch.object(t,'prerequisite',side_effect=ValueError('missing eligibility')):
                with self.assertRaises(ValueError): r.prepare(output)
            self.assertFalse(output.exists())

    def test_unverified_build_and_correctness_stop_before_commands(self):
        with patch.object(t,'prerequisite',return_value={}), patch.object(t,'phase_proof',side_effect=ValueError('absent proof')):
            with self.assertRaises(ValueError): r.build(t.PREPARED,t.BUILT)
            with self.assertRaises(ValueError): q.qualify(t.BUILT,t.CORRECTNESS)
        with patch.object(x,'validate_request'),patch.object(x.v,'prerequisite',side_effect=ValueError('failed proof')):
            with self.assertRaises(ValueError): x.execute(t.BUILT,t.CORRECTNESS,t.EXECUTION)

    def test_arm_builds_and_independent_schedule_agree(self):
        rows=r.build_commands(t.PREPARED,t.BUILT)
        self.assertEqual(rows,v.expected_build_commands(t.PREPARED,t.BUILT))
        for arm in t.ARMS:
            self.assertTrue(any(row['name']==arm+'-thumbnails-compile' for row in rows))
            self.assertTrue(any(row['name']==arm+'-browser-compile' for row in rows))
        for row in rows:
            if '--build' in row['argv']:
                self.assertEqual(row['argv'][-2:],['--parallel','4'])

    def test_source_only_private_encoding_and_synchronous_publication(self):
        before=(t.Q/'C/source'/t.SERVICE).read_text()
        after=t.transform(before)
        self.assertEqual(after.replace('#include <QSaveFile>\n#include <QImageWriter>\n'+v.DETECTOR,'#include <QSaveFile>').replace(v.WRITER,v.ANCHOR),before)
        self.assertNotIn('pixelsPublished',after)
        self.assertIn('EXPECT_FALSE(progressive);',(DIRECTORY/'native/main.cpp').read_text())

    def test_exact_202_process_schedule(self):
        rows=t.schedule()
        self.assertEqual(len(rows),202)
        self.assertEqual(sum(row['warmup'] for row in rows),2)
        self.assertEqual([row['arm'] for row in rows[:2]],list(t.ARMS))
        for block in range(10):
            group=[row for row in rows if row['block']==block]
            order=t.ARMS if block%2==0 else t.ARMS[::-1]
            self.assertEqual([row['arm'] for row in group],[order[0]]*10+[order[1]]*10)

    def observations(self):
        return [dict(schedule=row,sample=dict(first_ms=10000 if row['warmup'] else 20 if row['arm']=='control' else 10,
            final_ms=10000 if row['warmup'] else 30 if row['arm']=='control' else 20)) for row in t.schedule()]

    def test_startup_statistics_warmups_and_stop_gate(self):
        rows=self.observations()
        expected=t.statistics_for(rows,True)
        self.assertEqual(expected,vx.summarize(rows,True))
        self.assertEqual(expected['decision'],'Recommend')
        self.assertEqual(expected['populations']['control']['first_ms']['p95'],20)
        self.assertEqual(vx.summarize(rows,False)['decision'],'Evidence insufficient')
        self.assertEqual(vx.summarize(rows[:-1],False)['decision'],'Evidence insufficient')
        for row in rows:
            if row['schedule']['arm']=='candidate' and not row['schedule']['warmup']:
                row['sample'].update(first_ms=16,final_ms=26)
        self.assertEqual(vx.summarize(rows,True)['decision'],'Deferred')

    def test_phase_growth_does_not_invalidate_prior_captured_membership(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/'tools').mkdir()
            source=root/'captured.py'; source.write_text('frozen')
            recorded={str(source):t.h.digest(source)}
            (root/'tools'/t.snapshot_name(source)).write_bytes(source.read_bytes())
            t.h.write(root/'tools.json',recorded)
            t.h.write(root/'integrity.json',dict(unchanged=True))
            with patch.object(t,'tools',return_value=dict(recorded,added='later')):
                v.tools(root)
            source.write_text('drift')
            with self.assertRaises(ValueError): v.tools(root)


if __name__=='__main__': unittest.main()
