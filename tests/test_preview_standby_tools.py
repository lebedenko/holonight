"""The bounded experiment must not promote inconclusive or failed evidence."""
import importlib.util
import json
import os
from pathlib import Path
import pwd
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('standby', ROOT / 'scripts/measure-preview-standby.py')
standby = importlib.util.module_from_spec(spec)
spec.loader.exec_module(standby)


class StartupPilot(unittest.TestCase):
    def records(self):
        return {(label, fixture): [dict(first_ms=value, final_ms=value + .01) for _ in range(100)]
                for fixture in standby.measurement.FIXTURES
                for label, value in (('A', 100), ('B', 100), ('C', 115), ('D', 105))}

    def test_improvement_and_all_startup_gates_are_required(self):
        records = self.records()
        self.assertTrue(standby.pilot_assessment(records)['passed'])
        records[('D', 'oriented.jpg')][-10:] = [dict(first_ms=111, final_ms=111.01)] * 10
        self.assertFalse(standby.pilot_assessment(records)['passed'])

    def test_gate_pass_without_improvement_does_not_promote_candidate(self):
        records = self.records()
        records[('C', '3200x2400.png')] = records[('D', '3200x2400.png')]
        self.assertFalse(standby.pilot_assessment(records)['passed'])

    def test_metadata_failure_is_not_hidden_by_pixels(self):
        records = self.records()
        records[('D', '160x80.png')][-10:] = [dict(first_ms=105, final_ms=111)] * 10
        self.assertFalse(standby.pilot_assessment(records)['passed'])


class CorrelatedTrace(unittest.TestCase):
    def analyze(self, service='service', slot=1, request='0'):
        events = []
        def event(ns, phase, edge, tid=1, obj='service', worker=0, req='0'):
            events.append(dict(ns=ns, phase=phase, edge=edge, pid=123, tid=tid,
                               object=obj, slot=worker, request=req))
        event(0, 'pool_job', 'begin')
        event(10, 'inspect_exchange_including_transport', 'begin', obj='execution')
        event(20, 'pool_worker_prepare', 'begin', tid=2, obj=service, worker=slot, req=request)
        event(30, 'pool_worker_prepare', 'end', tid=2, obj=service, worker=slot, req=request)
        event(40, 'inspect_exchange_including_transport', 'end', obj='execution')
        event(50, 'pool_job', 'end')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'block.log'
            path.write_text(''.join('TRACE ' + json.dumps(e) + '\n' for e in events))
            return standby.trace_overlap([path])

    def test_overlapping_standby_is_correlated_to_service_and_slot(self):
        result = self.analyze()
        self.assertEqual(result['overlapping_requests'], 1)
        self.assertEqual(result['requests'][0]['overlap_ms'], .00001)

    def test_previous_service_and_demand_preparation_are_excluded(self):
        self.assertEqual(self.analyze(service='old-service')['overlapping_requests'], 0)
        self.assertEqual(self.analyze(slot=0)['overlapping_requests'], 0)

    def test_thread_context_survives_next_sample_label(self):
        self.assertEqual(self.analyze(request='1')['overlapping_requests'], 1)


class ObservationOwnership(unittest.TestCase):
    def test_harness_can_write_to_wrapper_created_observation_directory(self):
        uid = int(os.environ.get('SUDO_UID', '1000')) if os.geteuid() == 0 else os.geteuid()
        gid = pwd.getpwuid(uid).pw_gid
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            os.chown(output, uid, gid)
            target = standby.observation_directory(output, 'diagnostic', uid, gid)
            kwargs = dict(user=uid, group=gid, extra_groups=[]) if os.geteuid() == 0 else {}
            subprocess.run([sys.executable, '-c',
                            'from pathlib import Path; import sys; Path(sys.argv[1]).write_text("saved")',
                            str(target / 'sample.json')], check=True, **kwargs)
            self.assertEqual((target / 'sample.json').read_text(), 'saved')


if __name__ == '__main__':
    unittest.main()
