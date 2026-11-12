#!/usr/bin/env python3
"""Freeze private standby-deferral overlays; never modify qualification inputs.

Build four instrumented variants and one uninstrumented candidate against host
dependencies. Existing uninstrumented A-fixed/B/C binaries are inventoried for
the single startup pilot, rather than needlessly rebuilt.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LABELS = ('A', 'B', 'C', 'D')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(path):
    return {str(p.relative_to(path)): digest(p) for p in sorted(path.rglob('*')) if p.is_file()}


def replace(path, before, after):
    text = path.read_text()
    if text.count(before) != 1:
        raise RuntimeError(f'overlay anchor is not unique: {path}: {before}')
    path.write_text(text.replace(before, after))


def defer(source):
    path = source / 'holonight-file-browser/src/preview/session_pool.cpp'
    replace(path, '  bool stopping = false;',
            '  bool initial_window = true;\n  bool initial_active = false;\n  bool stopping = false;')
    replace(path, '      workers.at(index).used = true;',
            '      workers.at(index).used = true;\n'
            '      if (initial_window) { initial_active = true; return; }')
    replace(path, '    auto& target = workers.at(index);\n    if (cleanup_status',
            '    const bool deferred = initial_active;\n'
            '    if (deferred) { initial_active = false; initial_window = false; }\n'
            '    auto& target = workers.at(index);\n    if (cleanup_status')
    replace(path, '    schedule();\n  }\n  void executeJob',
            '    schedule();\n'
            '    if (deferred && result == RuntimeStatus::Success && !cancel->load() &&\n'
            '        cleanup_status == RuntimeStatus::Success && target.epoch == epoch &&\n'
            '        !occupied() && !pending && !disabled && !stopping &&\n'
            '        (!owner || !owner->launchesDisabled())) {\n'
            '      for (size_t standby = 0; standby < workers.size(); ++standby) {\n'
            '        if (standby != index && workers.at(standby).phase == Phase::Empty &&\n'
            '            (!workers.at(standby).failed || workers.at(standby).failed_demand != demand)) {\n'
            '          prepare(standby);\n'
            '        }\n'
            '      }\n'
            '    }\n  }\n  void executeJob')


HEADER = r'''#pragma once
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <unistd.h>
#include <sys/syscall.h>
namespace StandbyTrace {
inline void event(const char* phase, const char* edge, const void* object = nullptr, long slot = -1) {
  timespec t{}; clock_gettime(CLOCK_MONOTONIC, &t);
  const auto* sample = std::getenv("STANDBY_SAMPLE");
  char line[512];
  int n = std::snprintf(line, sizeof(line), "TRACE {\"ns\":%lld,\"pid\":%d,\"tid\":%ld,\"request\":\"%s\",\"object\":\"%p\",\"slot\":%ld,\"phase\":\"%s\",\"edge\":\"%s\"}\n",
    static_cast<long long>(t.tv_sec)*1000000000LL+t.tv_nsec, getpid(), syscall(SYS_gettid), sample ? sample : "setup", object, slot, phase, edge);
  if (n > 0 && n < static_cast<int>(sizeof(line))) { auto ignored = write(2, line, n); (void)ignored; }
}
struct Scope {
  const char* phase; const void* object; long slot;
  Scope(const char* p, const void* o = nullptr, long s = -1): phase(p), object(o), slot(s) {event(phase,"begin",object,slot);}
  ~Scope() {event(phase,"end",object,slot);}
};
}
'''


def instrument(source, harness, header):
    def scope(relative, anchor, phase, context='nullptr', slot='-1'):
        path = source / relative
        text = path.read_text()
        include = f'#include "{header}"\n'
        if include not in text:
            path.write_text(include + text)
        replace(path, anchor, anchor + f'\n  StandbyTrace::Scope trace("{phase}", {context}, {slot});')
    images = 'holonight-images/src/isolated/'
    scope(images + 'capture.cpp', 'CaptureResult capture(QIODevice& device, qint64 limit, const std::atomic_bool& cancelled) {', 'source_capture', '&device')
    scope(images + 'verification.cpp', 'QStringList verifyRuntime(const QString& root) {', 'runtime_validation', '&root')
    generation = source / (images + 'generation.cpp')
    if generation.exists():
        scope(images + 'generation.cpp', 'GenerationLease RuntimeOwner::acquire() const {', 'generation_acquisition', 'this')
        scope(images + 'generation.cpp', 'bool RuntimeOwner::refresh() {', 'generation_validation', 'this')
    path = source / (images + 'runtime.cpp')
    context = 'this'
    if '  void launch() {' in path.read_text():
        scope(images + 'runtime.cpp', '  void launch() {', 'helper_prepare', 'this')
        scope(images + 'runtime.cpp', '  void retire() {', 'cleanup', 'this')
        replace(path, '    prepared = true;', '    StandbyTrace::event("helper_ready", "point", this);\n    prepared = true;')
    else:
        context = '&process'
        path.write_text(f'#include "{header}"\n' + path.read_text())
        replace(path, '    QStringList binds;', '    StandbyTrace::event("helper_prepare", "begin", &process);\n    QStringList binds;')
        replace(path, '    result.startup = elapsed.elapsed();', '    StandbyTrace::event("helper_ready", "point", &process);\n    StandbyTrace::event("helper_prepare", "end", &process);\n    result.startup = elapsed.elapsed();')
        replace(path, '    NativeCleanup operations(process);', '    StandbyTrace::Scope trace("cleanup", &process);\n    NativeCleanup operations(process);')
    replace(path, 'auto exchange = [&](const Request& command, const QByteArray& data, bool retained) {',
            'auto exchange = [&](const Request& command, const QByteArray& data, bool retained) {\n'
            f'      StandbyTrace::Scope trace(command.operation == Operation::Decode ? "decode_exchange_including_transport" : "inspect_exchange_including_transport", {context});')
    browser = 'holonight-file-browser/src/preview/'
    scope(browser + 'preview_service.cpp', '      cache_(std::make_shared<PreviewWorkerCache>()) {', 'service_construction', 'this')
    pool = source / (browser + 'session_pool.cpp')
    if pool.exists():
        scope(browser + 'session_pool.cpp', '  void prepare(size_t index) {', 'pool_prepare', 'control', 'index')
        scope(browser + 'session_pool.cpp', '        [this, index, lease, cancel, preparing_epoch, preparing_demand] {', 'pool_worker_prepare', 'control', 'index')
        scope(browser + 'session_pool.cpp', '  void transactionStarted(size_t index) {', 'transaction_dispatch', 'control', 'index')
        scope(browser + 'session_pool.cpp', '  void executeJob(size_t index, const GenerationLease& lease, const Pending& job) {', 'pool_job', 'control', 'index')
        scope(browser + 'session_pool.cpp', '  void shutdown() {', 'pool_shutdown', 'control')
    path = harness / 'reuse.cpp'
    path.write_text(f'#include "{header}"\n' + path.read_text())
    replace(path, '  for (int number = 0; number < count; ++number) {',
            '  for (int number = 0; number < count; ++number) {\n'
            '    const auto trace_sample = QByteArray::number(number);\n'
            '    setenv("STANDBY_SAMPLE", trace_sample.constData(), 1);')
    replace(path, '        pixel_delivered = true;', '        StandbyTrace::event("pixels", "point", service.get());\n        pixel_delivered = true;')
    replace(path, '        final_delivered = true;', '        StandbyTrace::event("metadata", "point", service.get());\n        final_delivered = true;')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('previous', type=Path)
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    previous = args.previous.resolve()
    frozen = json.loads((previous / 'freeze.json').read_text())
    for label in LABELS[:3]:
        if inventory(previous / label / 'source') != frozen['source_inventories'][label]:
            raise RuntimeError(f'frozen source identity mismatch: {label}')
    for key, command in (('compiler', ['c++', '--version']),
                         ('dependencies', ['pkg-config', '--modversion', 'Qt6Core', 'libexif', 'libwebp'])):
        if subprocess.check_output(command, text=True) != frozen[key]:
            raise RuntimeError(f'host environment changed: {key}')
    output = Path(tempfile.mkdtemp(prefix='preview-standby-', dir=ROOT / 'build'))
    print(output, flush=True)
    shutil.copy2(__file__, output / 'prepare.py')
    header = output / 'trace.h'
    header.write_text(HEADER)
    fixtures = ROOT / 'build/preview-transaction-20261111-144758/fixtures'
    prereg = {'previous': str(previous), 'reference': 'A-fixed', 'labels': {'A': 'A-fixed', 'B': 'B', 'C': 'unchanged C', 'D': 'initial standby deferral'},
              'samples': 100, 'warmups': 1, 'block_size': 10, 'order': 'rotate A/B/C/D each block',
              'scenarios': ['startup'], 'fixtures': {p.name: digest(p) for p in fixtures.iterdir() if p.is_file()},
              'stop': 'one diagnostic and one pilot only; any invalid observation, unverified cleanup, inconclusive overlap, either large-PNG p95 not improved or any startup gate failed stops correction',
              'exchange_durations': 'include transport overhead', 'qualification': False,
              'compiler': frozen['compiler'], 'dependencies': frozen['dependencies']}
    (output / 'preregistration.json').write_text(json.dumps(prereg, indent=2) + '\n')
    # Keep original binaries for the uninstrumented pilot; no old input is changed.
    builds = [('diagnostic', label) for label in LABELS] + [('pilot', 'D')]
    for mode, label in builds:
        base = output / mode / label
        base.mkdir(parents=True)
        shutil.copytree(previous / ('C' if label == 'D' else label) / 'source', base / 'source')
        shutil.copytree(previous / 'harness-source', base / 'harness-source')
        if label == 'D':
            defer(base / 'source')
        if mode == 'diagnostic':
            instrument(base / 'source', base / 'harness-source', header)
        (base / 'source-inventory.json').write_text(json.dumps(inventory(base / 'source'), indent=2) + '\n')
        with (base / 'build.log').open('x') as log:
            def run(*command):
                command = list(map(str, command))
                log.write(json.dumps(command) + '\n'); log.flush()
                subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
            prefix = base / 'prefix'
            for repo in ('holonight-images', 'holonight-thumbnails', 'holonight-file-browser'):
                binary = base / 'build' / repo
                if repo == 'holonight-images':
                    flags = ['-DHOLONIGHT_IMAGES_ISOLATED=ON', f'-DHOLONIGHT_IMAGES_RUNTIME_BUNDLE={base / "runtime"}']
                elif repo == 'holonight-thumbnails':
                    flags = ['-DHOLONIGHT_THUMBNAILS_ISOLATED=ON']
                else:
                    flags = [f'-DBUILD_FILE_BROWSER_{c}=OFF' for c in ('QUICK', 'SEARCH', 'STORAGE', 'PREVIEW_QUICK', 'MARKDOWN')]
                run('cmake', '-S', base / 'source' / repo, '-B', binary, '-G', 'Ninja',
                    '-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=OFF', f'-DCMAKE_INSTALL_PREFIX={prefix}',
                    f'-DCMAKE_PREFIX_PATH={prefix}', *flags)
                run('cmake', '--build', binary, '--parallel', args.jobs)
                if repo == 'holonight-images':
                    run('python3', base / 'source' / repo / 'scripts/prepare-isolated-runtime.py',
                        '--helper', binary / 'holonight-images-helper', '--plugins', '/usr/lib/qt6/plugins', '--output', base / 'runtime')
                run('cmake', '--install', binary)
            run('cmake', '-S', base / 'harness-source', '-B', base / 'reuse-harness', '-G', 'Ninja',
                '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_PREFIX_PATH={prefix}', '-DPREVIEW_REUSE_BENCHMARK=ON',
                f'-DREUSABLE_VARIANT={"ON" if label in ("C", "D") else "OFF"}')
            run('cmake', '--build', base / 'reuse-harness', '--parallel', args.jobs)
        (base / 'binary-inventory.json').write_text(json.dumps({str(p.relative_to(base)): digest(p) for p in
            (base / 'reuse-harness/preview-benchmark', base / 'build/holonight-images/holonight-images-helper')}, indent=2) + '\n')
        print(mode, label, 'built', flush=True)
    (output / 'ready.json').write_text(json.dumps({'previous': str(previous), 'fixtures': str(fixtures)}) + '\n')


if __name__ == '__main__':
    main()
