"""Evidence accounting must not hide failed requests or missing observations."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import zlib


ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


measure = module('measure-preview-experiments')
baselines = module('preview-experiment-baselines')


class EvidenceAccounting(unittest.TestCase):
    def test_failed_requests_remain_in_denominator(self):
        records = [dict(success=True, setup_success=True, harness_timeout=False,
                        superseded_selections=20, first_ms=2, final_ms=4, wall_ms=5),
                   dict(success=False, setup_success=False, harness_timeout=True,
                        superseded_selections=20, first_ms=-1, final_ms=-1, wall_ms=10000,
                        error='deadline exceeded')]
        result = measure.summary(records)
        self.assertEqual(result['samples'], 2)
        self.assertEqual(result['failures'], 1)
        self.assertEqual(result['setup_failures'], 1)
        self.assertEqual(result['harness_timeouts'], 1)
        self.assertEqual(result['first_ms']['missing'], 1)
        self.assertEqual(result['final_ms']['observations'], 1)
        self.assertEqual(result['wall_ms']['maximum'], 10000)
        self.assertEqual(result['superseded_selections'], 40)
        self.assertEqual(result['reported_errors'], {'deadline exceeded': 1})

    def test_all_missing_pixels_have_no_latency_statistic(self):
        result = measure.summary([dict(success=False, setup_success=True, harness_timeout=False,
                                       superseded_selections=0, first_ms=-1, final_ms=8, wall_ms=9)])
        self.assertIsNone(result['first_ms']['median'])
        self.assertIsNone(result['first_ms']['p95'])
        self.assertIsNone(result['first_ms']['maximum'])
        self.assertEqual(result['final_ms']['median'], 8)

    def test_idle_pane_completion_without_upgraded_pixels_is_invalid(self):
        result = measure.summary([dict(success=True, setup_success=True, harness_timeout=False,
                                       superseded_selections=0, first_ms=-1, final_ms=.002, wall_ms=.003)])
        self.assertEqual(result['invalid_success_observations'], 1)
        self.assertEqual(result['first_ms']['missing'], 1)
        self.assertIsNone(result['first_ms']['median'])

    def test_p95_uses_nearest_rank_and_preserves_maximum(self):
        records = [dict(success=True, setup_success=True, harness_timeout=False,
                        superseded_selections=0, first_ms=i, final_ms=i, wall_ms=i) for i in range(1, 101)]
        result = measure.summary(records)
        self.assertEqual(result['first_ms']['median'], 50.5)
        self.assertEqual(result['first_ms']['p95'], 95)
        self.assertEqual(result['first_ms']['maximum'], 100)

    def test_inventory_detects_bytes_modes_and_symlink_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / 'artifact'
            path.write_bytes(b'one')
            before = baselines.inventory(root)
            path.write_bytes(b'two')
            self.assertNotEqual(before, baselines.inventory(root))
            before = baselines.inventory(root)
            path.chmod(0o700)
            self.assertNotEqual(before, baselines.inventory(root))
            before = baselines.inventory(root)
            path.unlink()
            path.symlink_to('missing')
            self.assertNotEqual(before, baselines.inventory(root))

    def test_fixture_is_valid_deterministic_rgb_png(self):
        data = measure.png(3, 2)
        self.assertEqual(data, measure.png(3, 2))
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        offset = 8
        chunks = {}
        while offset < len(data):
            length = struct.unpack('>I', data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            payload = data[offset + 8:offset + 8 + length]
            crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
            self.assertEqual(crc, zlib.crc32(kind + payload))
            chunks[kind] = payload
            offset += 12 + length
        self.assertEqual(struct.unpack('>IIBBBBB', chunks[b'IHDR']), (3, 2, 8, 2, 0, 0, 0))
        self.assertEqual(zlib.decompress(chunks[b'IDAT']), (b'\0' + b'\xff\0\0' * 3) * 2)
        self.assertNotEqual(measure.png(3, 2), measure.png(3, 2, True))


if __name__ == '__main__':
    unittest.main()
