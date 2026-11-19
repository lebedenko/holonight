"""Process-forbidden regressions for askpass and root-side build verification."""
import importlib.util
from pathlib import Path
import pwd
import runpy
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

DIRECTORY=Path(__file__).resolve().parents[1]/'tooling/preview-cache-complexity-encoding-trial/qualification-rerun-05'


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeFixtureTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess,'Popen',side_effect=AssertionError('process forbidden')))
        self.enterContext(patch.object(subprocess,'run',side_effect=AssertionError('process forbidden')))
        previous=dict(sys.modules)
        old_path=list(sys.path)
        self.addCleanup(lambda:sys.path.__setitem__(slice(None),old_path))
        self.addCleanup(lambda: [sys.modules.pop(key,None) for key in set(sys.modules)-set(previous)])
        sys.path.insert(0,str(DIRECTORY))
        for key in ('contract','correctness','stage','qualify'):
            old=sys.modules.pop(key,None)
            if old is not None: self.addCleanup(lambda k=key,v=old:sys.modules.__setitem__(k,v))
        self.module=load('rerun_test_interface',DIRECTORY/'correctness_phase.py')

    def test_provider_fixture_runtime_and_protected_session_are_distinct(self):
        c=self.module
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            rows=c.schedule(c.c.t.BUILT,root)
            verifier=load('fixture_path_verifier',DIRECTORY/'offline/verify_correctness_phase.py')
            c.h.write(root/'schedule.json',rows)
            verifier.base.verify_schedule(root,c.c.t.BUILT,c.c.protocol())
            for row in rows:
                if row['name'].endswith('-holonight-file-browser-configure'):
                    flat=c.c.t.BUILT/row['arm']/'runtime'
                    self.assertIn('-DHOLONIGHT_FILE_BROWSER_TEST_RUNTIME='+str(flat),row['argv'])
                    self.assertNotEqual(row['environment']['HN_BROWSER_SESSION_RUNTIME'],str(flat))

    def test_root_verification_uses_build_owner_environment(self):
        verifier=load('rerun_test_build_verifier',DIRECTORY/'offline/verify.py')
        original=SimpleNamespace(DIRECTORY=DIRECTORY,environment=lambda:{'HOME':'/root'})
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            expected_home=pwd.getpwuid(root.stat().st_uid).pw_dir
            def verify(path):
                self.assertEqual(original.environment()['HOME'],expected_home)
                self.assertEqual(original.environment()['XDG_RUNTIME_DIR'],'/run/user/'+str(root.stat().st_uid))
                return {'status':'passed'}
            with patch.object(verifier.t.e,'load',side_effect=[original,SimpleNamespace(verify=verify)]),patch('os.getuid',return_value=0):
                self.assertEqual(verifier.verify(root),{'status':'passed'})

    def test_askpass_precedes_trial_in_same_process(self):
        base=self.module.base
        events=[]
        def authenticate(argv,check):
            self.assertEqual(argv,['sudo','-A','-v'])
            self.assertTrue(check)
            events.append('askpass')
        def qualify(*args):
            events.append('qualify')
            return {'status':'qualified'}
        argv=['correctness_phase.py','--askpass','--built','/tmp/built','--output','/tmp/output']
        with patch.object(sys,'argv',argv),patch.object(base.c.t,'prerequisite'),patch.object(base.c.t,'phase_proof'), \
             patch.object(base,'validate_request'),patch.object(base.subprocess,'run',side_effect=authenticate), \
             patch.object(base,'qualify',side_effect=qualify):
            with self.assertRaises(SystemExit) as exited:
                runpy.run_path(str(DIRECTORY/'correctness_phase.py'),run_name='__main__')
        self.assertEqual(exited.exception.code,0)
        self.assertEqual(events,['askpass','qualify'])


if __name__=='__main__': unittest.main()
