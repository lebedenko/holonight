#!/usr/bin/env python3
"""Verify staged production authentication runtime evidence without PAM or desktop input."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kit', type=Path)
    parser.add_argument('--logs', type=Path, required=True)
    args = parser.parse_args()
    kit = args.kit.resolve()
    sys.path.insert(0, str(kit))
    spec = importlib.util.spec_from_file_location('authentication_test', kit / 'authentication-test.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    assert os.environ.get('QT_QPA_PLATFORM') == 'offscreen', 'use the private test runner'
    for style in ('Holonight', 'Fusion'):
        for scale in ('1', '1.25'):
            tag = f'{style}-{scale}'
            case = args.logs / ('askpass-' + tag)
            case.mkdir(exist_ok=False)
            env = helper.runtime_environment(case, style, scale)
            env.update(QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software')
            with (case / 'process.log').open('w') as log:
                child = subprocess.Popen([str(kit / 'prefix/bin/holonight-sudo-askpass'), 'Synthetic staging inspection'],
                                         env=env, stdout=subprocess.PIPE, stderr=log)
                try:
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        assert child.poll() is None, 'Askpass exited before runtime inspection'
                        text = (case / 'process.log').read_text(errors='replace')
                        if 'phase=implementation' in text:
                            break
                        time.sleep(0.05)
                    else:
                        raise AssertionError('missing actual Askpass UI evidence')
                    metadata = dict(pid=child.pid, style=style, scale=scale)
                finally:
                    child.terminate()
                    stdout, _ = child.communicate(timeout=5)
                assert stdout == b'', 'Askpass wrote protocol data without a response'
                helper.runtime_evidence(case, metadata)
                evidence = json.loads((case / 'runtime.json').read_text())
                assert evidence['verified'], evidence
                helper.write_json(case / 'process.json', dict(metadata, exit_status=child.returncode,
                    outcome='normal-exit' if child.returncode >= 0 else 'signal-exit', stdout_bytes=len(stdout)))
            case = args.logs / ('polkit-' + tag)
            case.mkdir(exist_ok=False)
            text = (args.logs / ('installed-' + tag + '.log')).read_text()
            (case / 'process.log').write_text(text)
            pid = int(re.search(r'^\s*(\d+):', text, re.M)[1])
            helper.runtime_evidence(case, dict(pid=pid, style=style, scale=scale))
            evidence = json.loads((case / 'runtime.json').read_text())
            assert evidence['verified'], evidence
            print('PASS: staged actual style, scale and modules:', tag, flush=True)


if __name__ == '__main__':
    main()
