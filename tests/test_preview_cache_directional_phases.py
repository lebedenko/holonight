"""Process-forbidden writable-provider phase and independent schedule tests."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/'tooling/preview-cache-complexity-encoding-trial/qualification'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

previous={key:sys.modules.get(key) for key in ('contract','correctness','stage','qualify','execute')}
sys.path.insert(0,str(DIRECTORY))
c=load('writable_correctness',DIRECTORY/'correctness_phase.py')
v=load('writable_correctness_verifier',DIRECTORY/'offline/verify_correctness_phase.py')
x=load('writable_startup',DIRECTORY/'execute_phase.py')
sys.path.remove(str(DIRECTORY))
for key,value in previous.items():
    if value is None: sys.modules.pop(key,None)
    else: sys.modules[key]=value


class PhaseTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess,'Popen',side_effect=AssertionError('process forbidden')))
        self.enterContext(patch.object(subprocess,'run',side_effect=AssertionError('process forbidden')))

    def test_independent_schedule_and_sealed_build_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)
            rows=c.schedule(c.c.t.BUILT,output)
            self.assertEqual(len(rows),72)
            c.h.write(output/'schedule.json',rows)
            self.assertEqual(v.base.verify_schedule(output,c.c.t.BUILT,c.c.protocol()),rows)
            for row in rows:
                if row['name'].endswith('-ctest'):
                    self.assertTrue(Path(row['argv'][2]).is_relative_to(output))
                if '--build' in row['argv']:
                    self.assertEqual(row['argv'][-2:],['--parallel','4'])

    def test_phase_rejects_absent_build_proof_before_output_creation(self):
        with patch.object(c.c.t,'prerequisite',return_value={}),patch.object(c.c.t,'phase_proof',side_effect=ValueError('absent proof')):
            with self.assertRaises(ValueError): c.qualify(c.c.t.BUILT,c.c.t.CORRECTNESS)

    def test_startup_requires_current_correctness_proof_before_processes(self):
        with patch.object(x.base,'validate_request'),patch.object(x.base.v,'prerequisite',side_effect=ValueError('not qualified')):
            with self.assertRaises(ValueError): x.execute(c.c.t.BUILT,c.c.t.CORRECTNESS,c.c.t.EXECUTION)


if __name__=='__main__': unittest.main()
