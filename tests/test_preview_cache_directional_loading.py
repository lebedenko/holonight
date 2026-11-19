"""Process-forbidden linkage and mapped-artifact regression checks."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

DIRECTORY=Path(__file__).resolve().parents[1]/'tooling/preview-cache-complexity-encoding-trial/qualification-rerun-06'


class LoadingTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(patch.object(subprocess,'Popen',side_effect=AssertionError('process forbidden')))
        self.enterContext(patch.object(subprocess,'run',side_effect=AssertionError('process forbidden')))
        previous=sys.modules.pop('contract',None)
        if previous is not None: self.addCleanup(lambda:sys.modules.__setitem__('contract',previous))
        else: self.addCleanup(lambda:sys.modules.pop('contract',None))
        sys.path.insert(0,str(DIRECTORY))
        self.addCleanup(lambda:sys.path.remove(str(DIRECTORY)))
        spec=importlib.util.spec_from_file_location('loading_regression_support',DIRECTORY/'offline/verify.py')
        self.support=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.support)
        self.temporary=tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)

    def test_linkage_export_retains_library_identities(self):
        library=self.root/'libfixture.so';library.write_bytes(b'fixture library')
        log=self.root/'ldd.stdout';log.write_text('libfixture.so => '+str(library)+' (0x123)\n')
        self.assertEqual(self.support.linkage(log),{str(library):self.support.t.h.digest(library)})

    def test_mapped_export_checks_inode_and_linked_bytes(self):
        binary=self.root/'consumer';binary.write_bytes(b'consumer')
        stat=binary.stat()
        mapping=f'0000-1000 r-xp 0000 {os.major(stat.st_dev):x}:{os.minor(stat.st_dev):x} {stat.st_ino} {binary}\n'
        record=dict(executable=str(binary),maps=mapping,helper_mappings='unavailable: helper exited before post-timing capture')
        expected={str(binary):self.support.t.h.digest(binary)}
        self.assertEqual(self.support.mapped(record,binary,expected),expected)
        with self.assertRaises(ValueError): self.support.mapped(record,binary,{str(binary):'changed digest'})
        record['maps']=mapping.replace(str(stat.st_ino)+' ',str(stat.st_ino+1)+' ')
        with self.assertRaises(ValueError): self.support.mapped(record,binary,expected)


if __name__=='__main__': unittest.main()
