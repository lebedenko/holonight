"""Pure copy/publication tests; privileged lifecycle is exercised separately."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('generations', Path(__file__).resolve().parents[1] /
                                            'scripts/manage-images-generations.py')
generations = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generations)


class GenerationCopy(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / 'source'
        self.destination = self.root / 'destination'
        self.source.mkdir()
        self.destination.mkdir()

    def test_copy_creates_distinct_inodes_and_old_open_alias_cannot_mutate_copy(self):
        original = self.source / 'file'
        original.write_bytes(b'original')
        original.chmod(0o644)
        with original.open('r+b') as alias:
            generations.copy_tree(self.source, self.destination)
            alias.write(b'modified')
        self.assertEqual((self.destination / 'file').read_bytes(), b'original')
        self.assertNotEqual(original.stat().st_ino, (self.destination / 'file').stat().st_ino)

    def test_rejects_symlinks_and_oversized_inventory(self):
        (self.source / 'alias').symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):
            generations.copy_tree(self.source, self.destination)
        (self.source / 'alias').unlink()
        for number in range(129):
            path = self.source / str(number)
            path.write_bytes(b'')
            path.chmod(0o644)
        with self.assertRaises(ValueError):
            generations.copy_tree(self.source, self.destination)

    def test_publication_never_replaces_existing_directory(self):
        with self.assertRaises(FileExistsError):
            generations.publish(self.source, self.destination)
        self.assertTrue(self.source.exists())
        self.destination.rmdir()
        generations.publish(self.source, self.destination)
        self.assertFalse(self.source.exists())

    def test_shared_lease_blocks_exclusive_removal_and_releases_on_exit(self):
        with generations.lease(self.source):
            with self.assertRaises(BlockingIOError):
                with generations.lease(self.source, exclusive=True):
                    self.fail('exclusive lease bypassed active reader')
        with generations.lease(self.source, exclusive=True):
            pass


if __name__ == '__main__':
    unittest.main()
