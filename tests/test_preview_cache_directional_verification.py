"""Process-forbidden final phase snapshot verification regressions."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

DIRECTORY=Path(__file__).resolve().parents[1]/'tooling/preview-cache-complexity-encoding-trial/qualification-rerun-06'


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess,'Popen',side_effect=AssertionError('process forbidden')))
        self.enterContext(patch.object(subprocess,'run',side_effect=AssertionError('process forbidden')))
        previous=sys.modules.pop('contract',None)
        if previous is None: self.addCleanup(lambda:sys.modules.pop('contract',None))
        else: self.addCleanup(lambda:sys.modules.__setitem__('contract',previous))
        sys.path.insert(0,str(DIRECTORY))
        self.addCleanup(lambda:sys.path.remove(str(DIRECTORY)))
        spec=importlib.util.spec_from_file_location('final_verification_regression',DIRECTORY/'offline/verify_execution_final.py')
        self.verifier=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.verifier)
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)
        (self.root/'tools').mkdir()
        self.source=self.root/'source.py'
        self.source.write_text('frozen source')
        t=self.verifier.t
        self.snapshot=self.root/'tools'/t.snapshot_name(self.source)
        self.snapshot.write_bytes(self.source.read_bytes())
        t.h.write(self.root/'tools.json',{str(self.source):t.h.digest(self.source)})
        t.h.write(self.root/'integrity.json',dict(unchanged=True))

    def test_later_membership_does_not_invalidate_captured_phase(self):
        (self.root/'later.py').write_text('later phase')
        snapshots=self.verifier.phase.base.support.tools(self.root)
        self.assertEqual(snapshots,{'tools/'+self.snapshot.name})

    def test_changed_captured_snapshot_rejected(self):
        self.snapshot.write_text('tampered')
        with self.assertRaises(ValueError): self.verifier.phase.base.support.tools(self.root)

    def test_changed_live_source_rejected(self):
        self.source.write_text('drift')
        with self.assertRaises(ValueError): self.verifier.phase.base.support.tools(self.root)


if __name__=='__main__': unittest.main()
