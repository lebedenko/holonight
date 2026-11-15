#!/usr/bin/env python3
"""Independent stdlib-only device-path audit checker; does not import the auditor."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile


def check(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            check(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def sealed(root):
    actual = {}
    for path in root.rglob('*'):
        check(not path.is_symlink(), 'symlink in evidence')
        if path.is_file() and path != root / 'seal.json':
            actual[str(path.relative_to(root))] = digest(path)
    check(actual == read(root / 'seal.json'), 'seal mismatch: ' + str(root))


def build_id(path):
    result = subprocess.check_output(['readelf', '-n', str(path)], text=True, timeout=30)
    ids = re.findall(r'Build ID: ([0-9a-f]+)', result)
    check(len(ids) == 1, 'missing/ambiguous build ID')
    return ids[0]


def bind(evidence, verification):
    sealed(evidence)
    passed = read(verification)
    check(passed['status'] == 'passed' and passed['evidence_seal'] == digest(evidence / 'seal.json') and
          (passed['measured_sweeps'], passed['warmup_sweeps'], passed['measured_rows'], passed['warmup_rows']) ==
          (125, 5, 7500, 300), 'independent verification binding mismatch')
    assessment = read(evidence / 'assessment.json')
    check(assessment['status'] == 'complete', 'incomplete diagnostic')
    identities = dict(read(evidence / 'inputs.json')['identities'])
    identities[str(evidence / 'seal.json')] = digest(evidence / 'seal.json')
    identities[str(verification)] = digest(verification)
    for name, expected in identities.items():
        path = Path(name)
        check(digest(path) == expected, 'consumed identity drift: ' + name)
        if path.name == 'seal.json':
            sealed(path.parent)
    return dict(evidence=str(evidence), verification=str(verification), identities=identities)


def check_accounting(root, saved):
    registration = read(root / 'preregistration.json')
    mapping = registration['mapping']
    check([f['ordinal'] for f in mapping] == list(range(len(mapping))), 'mapping ordinals')
    # Replay every raw row in fixed registered order, independently of auditor grouping.
    schedule = registration['schedule']
    cases = ('qt_device', 'qt_file', 'evp_file', 'qt_memory', 'evp_memory')
    expected_schedule = [dict(case=c, block=None, warmup=True, sweep=0) for c in cases]
    for block in range(5):
        for case in cases[block:] + cases[:block]:
            expected_schedule += [dict(case=case, block=block, warmup=False, sweep=s) for s in range(5)]
    check(schedule == [dict(index=i, **s) for i, s in enumerate(expected_schedule)], 'schedule drift')
    lines = iter((root / 'native.stdout').read_text().splitlines())
    check(json.loads(next(lines))['type'] == 'identity', 'missing native identity')
    sums = {(b, c, f['ordinal']): 0 for b in range(5) for c in cases[:2] for f in mapping}
    for sweep in schedule:
        duration = 0
        for f in mapping:
            row = json.loads(next(lines))
            check(row['type'] == 'file' and all(row[k] == value for k, value in sweep.items()) and
                  (row['ordinal'], row['bytes'], row['sha256']) == (f['ordinal'], f['size'], f['sha256']),
                  'missing/duplicate ordinal or raw schedule drift')
            check(all(type(row[k]) is int and row[k] > 0 for k in ('init_ns', 'update_ns', 'final_ns')), 'invalid raw duration')
            duration += sum(row[k] for k in ('init_ns', 'update_ns', 'final_ns'))
            if not sweep['warmup'] and sweep['case'] in cases[:2]:
                sums[sweep['block'], sweep['case'], f['ordinal']] += row['update_ns']
        end = json.loads(next(lines))
        check(end['type'] == 'sweep_end' and end['index'] == sweep['index'] and
              duration <= end['elapsed_ns'] <= 30000000000, 'sweep completion drift')
    check(next(lines, None) is None, 'extra raw rows')
    check(len(saved) == 5, 'accounting blocks')
    summary = read(root / 'summary.json')
    for b, block in enumerate(saved):
        check(block['block'] == b and block['sweeps_per_arm'] == 5 and len(block['files']) == len(mapping), 'block shape')
        device = streaming = contributions = 0
        for f, actual in zip(mapping, block['files']):
            d, s = (sums[b, c, f['ordinal']] for c in cases[:2])
            check(actual == dict(f, device_sum_ns=d, streaming_sum_ns=s, difference_sum_ns=d-s,
                                 difference_mean_ms=float(Fraction(d-s, 5000000))), 'per-file accounting mismatch')
            device += d
            streaming += s
            contributions += actual['difference_sum_ns']
        expected = dict(block=b, sweeps_per_arm=5, device_sum_ns=device, streaming_sum_ns=streaming,
                        device_mean_ms=float(Fraction(device, 5000000)), streaming_mean_ms=float(Fraction(streaming, 5000000)),
                        difference_mean_ms=float(Fraction(device-streaming, 5000000)),
                        throughput_ratio=float(Fraction(streaming, device)), files=block['files'])
        check(block == expected and contributions == device-streaming, 'block arithmetic/reconciliation mismatch')
        old = next(r for r in summary['ratios'] if r['block'] == b and r['numerator'] == 'qt_device' and r['denominator'] == 'qt_file')
        check(abs(old['ratio'] - block['throughput_ratio']) < 1e-15, 'retained throughput ratio drift')


def check_identity(root):
    identity = read(root / 'identity.json')
    check(digest(Path(identity['package'])) == identity['package_sha256'], 'package identity mismatch')
    check(digest(root / 'libQt6Core.so') == digest(Path(identity['host'])) == identity['host_sha256'], 'package/host mismatch')
    check(build_id(root / 'libQt6Core.so') == build_id(Path(identity['host'])) == identity['build_id'], 'package build ID mismatch')
    # Re-extract metadata and Qt bytes independently; a resealed substituted member must fail.
    for member, name in (('.BUILDINFO', 'BUILDINFO'), ('.PKGINFO', 'PKGINFO'), ('usr/lib/libQt6Core.so.6.12.0', 'libQt6Core.so')):
        data = subprocess.check_output(['bsdtar', '-xOf', identity['package'], member], timeout=60)
        check(data == (root / name).read_bytes(), 'package member mismatch: ' + member)
    check('pkgver = 6.12.0-5\n' in (root / 'BUILDINFO').read_text(), 'wrong package version')
    manifest = Path(identity['symbols_manifest'])
    check(digest(manifest) == identity['symbols_manifest_sha256'], 'debug manifest mismatch')
    check(read(manifest)['libQt6Core.so.6'] == identity['debug'], 'debug provenance mismatch')
    prepared = manifest.parent
    check(digest(prepared / 'seal.json') == identity['prepared_seal'], 'debug prepared binding mismatch')
    sealed(prepared)
    debug = identity['debug']
    check(digest(Path(debug['path'])) == debug['sha256'] and build_id(Path(debug['path'])) ==
          debug['build_id'] == identity['build_id'], 'debug identity mismatch')


def check_citations(root):
    for citation in read(root / 'citations.json'):
        path = root / citation['file']
        check(path.resolve().is_relative_to(root.resolve()), 'citation path escape')
        lines = path.read_text().splitlines()
        start, end = citation['start'], citation['end']
        check(digest(path) == citation['sha256'] and 1 <= start <= end <= len(lines) and
              '\n'.join(lines[start-1:end]) == citation['text'], 'citation drift')


def check_sources(root):
    provenance = read(root / 'source-provenance.json')
    check(provenance['status'] in ('exact', 'limited'), 'invalid source status')
    if provenance['status'] == 'limited':
        check(bool(provenance['limitation']), 'missing source limitation')
        if 'files' not in provenance:
            return
    recipe = (root / 'PKGBUILD').read_text()
    expected = re.search(r'^pkgbuild_sha256sum = ([0-9a-f]+)$', (root / 'BUILDINFO').read_text(), re.M).group(1)
    check(digest(root / 'PKGBUILD') == expected, 'recipe mismatch')
    checksums = re.findall(r"'([0-9a-f]{64})'", recipe.split('sha256sums=', 1)[1].split('prepare()', 1)[0])
    check(checksums[0] == provenance['archive_sha256'] and digest(root / 'qtbase.tar') == provenance['archive_actual_sha256'], 'source archive mismatch')
    check((digest(root / 'qtbase.tar') == checksums[0]) == (provenance['status'] == 'exact'), 'source status mismatch')
    packaging = str(root / provenance['packaging_cache'])
    qt = str(root / provenance['qt_cache'])
    check(subprocess.check_output(['git', '-C', packaging, 'show', provenance['packaging_revision'] + ':PKGBUILD'], timeout=30) == (root / 'PKGBUILD').read_bytes(), 'packaging revision mismatch')
    check(subprocess.check_output(['git', '-C', qt, 'rev-parse', provenance['qt_tag'] + '^{commit}'], text=True, timeout=30).strip() == provenance['qt_commit'], 'Qt revision mismatch')
    with tempfile.TemporaryFile() as archived:
        subprocess.run(['git', '-c', 'core.abbrev=no', '-C', qt, 'archive', '--format', 'tar', provenance['qt_tag']],
                       stdout=archived, stderr=subprocess.PIPE, timeout=180, check=True)
        archived.seek(0)
        check(hashlib.file_digest(archived, 'sha256').hexdigest() == provenance['archive_actual_sha256'], 'Git archive provenance mismatch')
    package_patches = re.findall(r'^  patch .* < (\S+)', recipe, re.M)
    commits = re.findall(r'cherry-pick -n ([0-9a-f]{40})', recipe)
    check(commits == provenance['cherry_picks'] and provenance['patches'] == package_patches + [c + '.patch' for c in commits], 'patch order drift')
    for name, expected in zip(package_patches, checksums[1:]):
        check(digest(root / name) == expected, 'package patch mismatch')
    for commit in commits:
        check(subprocess.check_output(['git', '-C', qt, 'diff', '--no-ext-diff', '--no-textconv', commit + '^', commit], timeout=30) == (root / (commit + '.patch')).read_bytes(), 'Qt patch revision mismatch')
    if not provenance['reconstructed']:
        check(provenance['status'] == 'limited' and not provenance['files'], 'missing source reconstruction')
        return
    # Reconstruct selected source independently from checksum-bound archive and retained patches.
    with tempfile.TemporaryDirectory() as tmp, tarfile.open(root / 'qtbase.tar') as archive:
        directory = Path(tmp)
        for name, expected in provenance['files'].items():
            check(not Path(name).is_absolute() and '..' not in Path(name).parts, 'source path escape')
            if name not in archive.getnames():
                continue  # A retained patch may introduce a new file.
            member = archive.getmember(name)
            check(member.isfile(), 'nonregular source')
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
        for name in provenance['patches']:
            subprocess.run(['patch', '--batch', '--forward', '-p1', '-d', str(directory), '-i', str((root / name).resolve())],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        for name, expected in provenance['files'].items():
            check(digest(directory / name) == expected == digest(root / 'source' / name), 'source reconstruction mismatch')


def verify(root):
    sealed(root)
    check(read(root / 'assessment.json')['status'] == 'complete', 'partial audit; no complete findings')
    inputs = read(root / 'inputs.json')
    check(bind(Path(inputs['evidence']), Path(inputs['verification'])) == inputs, 'input bindings drift')
    original = Path(inputs['evidence'])
    for name in ('native.stdout', 'preregistration.json', 'summary.json'):
        check(digest(root / name) == digest(original / name), 'raw snapshot drift')
    check(digest(root / 'source/harness.cpp') == digest(original / 'source/main.cpp'), 'harness drift')
    check_accounting(root, read(root / 'accounting.json'))
    check_identity(root)
    identity = read(root / 'identity.json')
    dep = read(original / 'inputs.json')['dependencies']['libQt6Core.so.6']
    check(identity['host'] == dep['host'] and identity['host_sha256'] == dep['host_sha256'] and
          identity['build_id'] == dep['build_id'], 'diagnostic Qt identity binding mismatch')
    prepared = Path(identity['symbols_manifest']).parent
    check(inputs['identities'][str(prepared / 'seal.json')] == identity['prepared_seal'], 'diagnostic debug binding mismatch')
    check_sources(root)
    check_citations(root)
    cited = {c['file'] for c in read(root / 'citations.json')}
    check('source/harness.cpp' in cited and all(str(p.relative_to(root)) in cited for p in (root / 'disassembly').iterdir() if p.suffix in ('.txt', '.range')), 'missing citations')
    identity = read(root / 'identity.json')
    expected_symbols = {'_ZN18QCryptographicHash7addDataEP9QIODevice', '_ZN9QIODevice4readEPcx',
                        '_ZN16QIODevicePrivate4readEPcxb', '_ZN11QFileDevice8readDataEPcx',
                        '_ZN13QFSFileEngine4readEPcx', '_ZNK11QFileDevice5atEndEv'}
    check({p.stem for p in (root / 'disassembly').glob('*.txt')} == expected_symbols, 'missing disassembly')
    for path in (root / 'disassembly').glob('*.txt'):
        symbol = path.stem
        actual = subprocess.check_output(['objdump', '-d', '--disassemble=' + symbol, identity['host']], timeout=30)
        check(actual == path.read_bytes() and ('<' + symbol + '@@').encode() in actual, 'disassembly drift/empty symbol')
    symbols = subprocess.check_output(['nm', '-S', identity['debug']['path']], timeout=30)
    check(symbols == (root / 'debug-symbols.txt').read_bytes(), 'debug symbol table drift')
    ranges = read(root / 'binary-ranges.json')
    check(any('QCryptographicHashPrivate' in r['symbol'] for r in ranges), 'missing private hash range')
    for item in ranges:
        expected_line = f"{item['start']:016x} {item['size']:016x} ".encode()
        check(any(line.startswith(expected_line) and line.endswith(item['symbol'].encode()) for line in symbols.splitlines()), 'private symbol binding mismatch')
        actual = subprocess.check_output(['objdump', '-d', '--start-address=' + hex(item['start']), '--stop-address=' + hex(item['start'] + item['size']), identity['host']], timeout=30)
        check(actual == (root / 'disassembly' / (item['symbol'] + '.range')).read_bytes(), 'private disassembly drift')
    sealed(root)
    return dict(status='passed', audit_seal=digest(root / 'seal.json'), source_status=read(root / 'source-provenance.json')['status'],
                blocks=5, ordinals=len(read(root / 'preregistration.json')['mapping']), imports_auditor=False, new_measurements=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    check(not args.output.exists() and not args.output.resolve().is_relative_to(args.evidence.resolve()), 'destination collision')
    try:
        result = verify(args.evidence.resolve())
    except (ValueError, OSError, KeyError, TypeError, IndexError, StopIteration, subprocess.SubprocessError) as error:
        result = dict(status='failed', failure=str(error))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(result)
    sys.exit(result['status'] != 'passed')
