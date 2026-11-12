#!/usr/bin/env python3
"""Prepare verified private v3 tracing sources only; never build or execute them."""
import argparse
import difflib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import hashlib

SPEC = importlib.util.spec_from_file_location('standby', Path(__file__).with_name('prepare-preview-standby-diagnostic.py'))
legacy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(legacy)
inventory = legacy.inventory
replace = legacy.replace

REVIEWED = {'A': {'source': 'dfa84a1bfc43afdcdee2e576930546889680bfca5c6a1c3f81aead44b4346275', 'harness-source': 'e7d6ad9ec634d2f3a39cdf52f7d128e3f070f9e9891ee7da81955f78b710f098'}, 'B': {'source': '1a79a537f601e7256b633ab315b8ff00442c2ef24dbc8514e73b36b2bed66e9d', 'harness-source': 'e7d6ad9ec634d2f3a39cdf52f7d128e3f070f9e9891ee7da81955f78b710f098'}, 'C': {'source': '78a9e28ba33ed3b60df020f7b925d8d4004fa980756385c260c103445d2bcbbb', 'harness-source': 'e7d6ad9ec634d2f3a39cdf52f7d128e3f070f9e9891ee7da81955f78b710f098'}, 'D': {'source': '9f0c97d3084fb90e6218aeed73edd3c3e330aedc63abfe7fb1d98ba875ec92cc', 'harness-source': 'e7d6ad9ec634d2f3a39cdf52f7d128e3f070f9e9891ee7da81955f78b710f098'}}

HEADER = r'''#pragma once
#include <atomic>
#include <cstdio>
#include <ctime>
#include <map>
#include <mutex>
#include <unistd.h>
#include <sys/syscall.h>
namespace StandbyTrace {
inline std::atomic<unsigned long long> sequence{1};
inline unsigned long long identity() { return sequence.fetch_add(1); }
struct Context {
  unsigned long long service=0, observation=0, job=0, worker=0, preparation=0;
  const char* role="setup";
};
inline thread_local Context current;
inline std::mutex contexts_mutex;
inline std::map<const void*, Context> contexts;
inline void remember(const void* object) { std::lock_guard<std::mutex> lock(contexts_mutex); contexts[object]=current; }
inline Context lifetime(const void* object) { std::lock_guard<std::mutex> lock(contexts_mutex); return contexts.at(object); }
inline void forget(const void* object) { std::lock_guard<std::mutex> lock(contexts_mutex); contexts.erase(object); }
struct Bind {
  Context previous;
  explicit Bind(Context value): previous(current) { current=value; }
  ~Bind() { current=previous; }
};
inline void event(const char* phase, const char* edge, const void* object=nullptr, long slot=-1) {
  timespec t{}; clock_gettime(CLOCK_MONOTONIC, &t);
  char line[1024];
  int n=std::snprintf(line,sizeof(line),"TRACE {\"version\":3,\"ns\":%lld,\"pid\":%d,\"tid\":%ld,\"request\":\"diagnostic\",\"object\":\"%p\",\"slot\":%ld,\"phase\":\"%s\",\"edge\":\"%s\",\"service\":%llu,\"observation\":%llu,\"job\":%llu,\"worker\":%llu,\"preparation\":%llu,\"role\":\"%s\"}\n",
    static_cast<long long>(t.tv_sec)*1000000000LL+t.tv_nsec,getpid(),syscall(SYS_gettid),object,slot,phase,edge,current.service,current.observation,current.job,current.worker,current.preparation,current.role);
  if(n>0 && n<static_cast<int>(sizeof(line))) { auto ignored=write(2,line,n); (void)ignored; }
}
struct Scope {
  const char* phase; const void* object; long slot; Context context;
  Scope(const char* p,const void* o=nullptr,long s=-1):phase(p),object(o),slot(s),context(current) { event(phase,"begin",object,slot); }
  ~Scope() { Bind bind(context); event(phase,"end",object,slot); }
};
}
'''


def capture(path, anchor):
    """One reviewed queued handoff; synchronous callbacks are never rewritten."""
    closing = anchor.index(']')
    replacement = (anchor[:closing] + ', trace_context = StandbyTrace::current' +
                   anchor[closing:].replace('{', '{\n          StandbyTrace::Bind trace_bind(trace_context);', 1))
    replace(path, anchor, replacement)


def propagate(path):
    # Exact reviewed handoffs shared by A/B/C/D. Each anchor must occur once.
    for anchor in (
        '[this, request, generation, revision, path, nativePath, cancel, beforeText, options] {',
        '[this, request, revision, result] {',
        '[this, path, nativePath, generation, cancel, size, beforeDispatch, beforeFull, stage, options, memoryCheckpoint] {',
        '[this, result] {',
        '[this] {\n              active_job_ = false;',
    ):
        capture(path, anchor)
    if path.with_name('session_pool.cpp').exists():
        for anchor in ('[this, directory] {',
                       '[this] {\n          if (sessions_) {',
                       '[this] {\n        if (sessions_) {\n          sessions_->shutdown();'):
            capture(path, anchor)
        capture(path, '[this] {\n        if (sessions_) {\n          sessions_->refresh();')


def overlay(base, header):
    source = base / 'source'
    # Saved diagnostic sources already contain the historical phase probes.
    for path in list(source.rglob('*.cpp')) + list((base / 'harness-source').glob('*.cpp')):
        text = path.read_text()
        text = re.sub(r'#include "[^"\n]*/trace.h"', '#include "' + str(header) + '"', text)
        path.write_text(text)
    browser = source / 'holonight-file-browser/src/preview'
    service = browser / 'preview_service.cpp'
    replace(service, '  pending_job_ = false;\n  active_job_ = true;',
            '  auto demand_context = StandbyTrace::lifetime(this);\n  demand_context.job = StandbyTrace::identity();\n  demand_context.worker = StandbyTrace::identity();\n  demand_context.role = "demand";\n  StandbyTrace::Bind demand_bind(demand_context);\n  StandbyTrace::Scope dispatch_trace("demand_dispatch", this);\n  pending_job_ = false;\n  active_job_ = true;')
    replace(service, '  StandbyTrace::Scope trace("service_construction", this, -1);',
            '  StandbyTrace::remember(this);\n  StandbyTrace::Scope trace("service_construction", this, -1);')
    replace(service, 'PreviewService::~PreviewService() {',
            'PreviewService::~PreviewService() {\n  StandbyTrace::Bind lifetime_bind(StandbyTrace::lifetime(this));\n  StandbyTrace::forget(this);\n  StandbyTrace::current.role = "shutdown";\n  StandbyTrace::Scope destruction_trace("service_destruction", this);')
    for anchor in ('connect(&timeout_timer_, &QTimer::timeout, this, [this] {',
                   'connect(&resize_debounce_timer_, &QTimer::timeout, this, [this] {'):
        replace(service, anchor, anchor + '\n    StandbyTrace::Bind lifetime_bind(StandbyTrace::lifetime(this));')
    replace(service, 'void PreviewService::shutdown() {',
            'void PreviewService::shutdown() {\n  StandbyTrace::Bind lifetime_bind(StandbyTrace::lifetime(this));\n  StandbyTrace::current.role = "shutdown";\n  StandbyTrace::Scope shutdown_trace("service_shutdown", this);')
    propagate(service)
    pool = browser / 'session_pool.cpp'
    if pool.exists():
        replace(pool, '    Failure failure;', '    Failure failure;\n    StandbyTrace::Context trace_context;')
        replace(pool, '.failure = std::move(failure)};', '.failure = std::move(failure), .trace_context = StandbyTrace::current};')
        replace(pool, '    if (pending->cancelled->load()) {',
                '    StandbyTrace::Bind demand_bind(pending->trace_context);\n    if (pending->cancelled->load()) {')
        replace(pool, '  void launch(size_t index) {',
                '  void launch(size_t index) {\n    StandbyTrace::Bind launch_bind(pending->trace_context);')
        replace(pool, '    auto job = std::move(*pending);', '    auto job = std::move(*pending);\n    StandbyTrace::Bind pending_bind(job.trace_context);')
        replace(pool, '    QThread thread;', '    unsigned long long trace_worker = StandbyTrace::identity();\n    unsigned long long trace_preparation = 0;\n    QThread thread;')
        replace(pool, '  Operations operations;', '  StandbyTrace::Context trace_lifetime = StandbyTrace::current;\n  Operations operations;')
        replace(pool, '  void prepare(size_t index) {', '  void prepare(size_t index, bool trace_standby = false) {')
        replace(pool, '    slot.phase = Phase::Preparing;', '    auto preparation_context = StandbyTrace::current;\n    preparation_context.job = trace_standby ? StandbyTrace::current.job : 0;\n    preparation_context.preparation = StandbyTrace::identity();\n    workers.at(index).trace_preparation = preparation_context.preparation;\n    preparation_context.worker = workers.at(index).trace_worker;\n    preparation_context.role = !preparation_context.observation ? "setup" : trace_standby ? "standby" : "demand";\n    StandbyTrace::Bind preparation_bind(preparation_context);\n    StandbyTrace::event("preparation_schedule", "point", control, index);\n    slot.phase = Phase::Preparing;')
        text = pool.read_text()
        if text.count('prepare(standby);') != (2 if 'bool initial_window = true;' in text else 1):
            raise RuntimeError('missing standby call anchor')
        pool.write_text(text.replace('prepare(standby);', 'prepare(standby, true);'))
        replace(pool, '  void executeJob(size_t index, const GenerationLease& lease, const Pending& job) {',
                '  void executeJob(size_t index, const GenerationLease& lease, const Pending& job) {\n    auto job_context = job.trace_context;\n    job_context.worker = workers.at(index).trace_worker;\n    job_context.preparation = workers.at(index).trace_preparation;\n    job_context.role = "demand";\n    StandbyTrace::Bind job_bind(job_context);')
        replace(pool, '  void shutdown() {', '  void shutdown() {\n    auto shutdown_context = trace_lifetime;\n    shutdown_context.role = "shutdown";\n    StandbyTrace::Bind shutdown_bind(shutdown_context);')
        replace(pool, '  SessionLifecycleResult close(size_t index) {', '  SessionLifecycleResult close(size_t index) {\n    auto cleanup_context = StandbyTrace::current;\n    cleanup_context.worker = workers.at(index).trace_worker;\n    cleanup_context.preparation = workers.at(index).trace_preparation;\n    StandbyTrace::Bind cleanup_bind(cleanup_context);\n    StandbyTrace::Scope cleanup_trace("worker_cleanup", control, index);')
        replace(pool, '    auto& slot = workers.at(index);\n    slot.phase = Phase::Active;',
                '    auto& slot = workers.at(index);\n    StandbyTrace::current.worker = slot.trace_worker;\n    StandbyTrace::current.preparation = slot.trace_preparation;\n    StandbyTrace::event("selected_worker", "point", control, index);\n    slot.phase = Phase::Active;')
        replace(pool, '  StandbyTrace::Scope trace("pool_worker_prepare", control, index);',
                '  StandbyTrace::event("pool_worker_prepare", "begin", control, index);')
        replace(pool, '          post([this, index, prepared, preparing_epoch, preparing_demand, idle_memory] {',
                '          StandbyTrace::event("pool_worker_prepare", "end", control, index);\n          post([this, index, prepared, preparing_epoch, preparing_demand, idle_memory] {')
        replace(pool, '      target.phase = Phase::Ready;',
                '      target.phase = Phase::Ready;\n      StandbyTrace::event("preparation_ready", "point", control, index);')
        replace(pool, '      maintain();', '      StandbyTrace::Bind lifetime_bind(trace_lifetime);\n      maintain();')
        for anchor in (
            '[this, lifetime, callback = std::move(callback)] {',
            '[this, index, lease, cancel, preparing_epoch, preparing_demand] {',
            '[this, index, prepared, preparing_epoch, preparing_demand, idle_memory] {',
            '[this, index] {\n          auto& target',
            '[this, index, retired] {', '[this, index, observing_epoch] {',
            '[this, index, observing_epoch, bytes] {',
            '[this, index] {\n      ++workers',
            '[this, index, has_session, poisoned, cleanup_status, ran, result, idle_memory, cancel = job.cancelled] {',
            '[this, index, lease, job = std::move(job)] {',
            '[this, index] {\n            close(index);',
        ):
            capture(pool, anchor)
    runtime = source / 'holonight-images/src/isolated/runtime.cpp'
    if 'class Execution::State {' in runtime.read_text():
        replace(runtime, '  std::function<void()> transaction_started;',
                '  StandbyTrace::Context trace_lifetime = StandbyTrace::current;\n  std::function<void()> transaction_started;')
        for anchor in (
            '      if (session && prepared && !active && process.bytesAvailable() != 0) {',
            '      if (session && prepared && !active) {',
        ):
            replace(runtime, anchor, anchor + '\n        auto idle_context = trace_lifetime;\n        idle_context.job = 0;\n        idle_context.role = "service_control";\n        StandbyTrace::Bind idle_bind(idle_context);')
    harness = base / 'harness-source/reuse.cpp'
    replace(harness, '    auto service = std::make_unique<PreviewService>',
            '    if (!StandbyTrace::current.service) StandbyTrace::current.service = StandbyTrace::identity();\n    auto construction_context = StandbyTrace::current;\n    construction_context.job = construction_context.worker = construction_context.preparation = 0;\n    construction_context.role = "service_control";\n    StandbyTrace::Bind construction_bind(construction_context);\n    StandbyTrace::event("construction_outer", "begin");\n    auto service = std::make_unique<PreviewService>')
    replace(harness, '    service->setRequestedSize(',
            '    StandbyTrace::event("construction_outer", "end", service.get());\n    StandbyTrace::event("construction_complete", "point", service.get());\n    service->setRequestedSize(')
    # A stable null object pairs the outer construction boundary across allocation.
    replace(harness, 'StandbyTrace::event("construction_outer", "end", service.get());',
            'StandbyTrace::event("construction_outer", "end");')
    replace(harness, '    QElapsedTimer clock;\n    clock.start();',
            '    StandbyTrace::current.service = StandbyTrace::identity();\n    StandbyTrace::current.observation = number + 1;\n    StandbyTrace::current.role = "demand";\n    StandbyTrace::event("startup_origin", "point");\n    QElapsedTimer clock;\n    clock.start();')


def prepare(previous, output, invocation):
    previous, output = previous.resolve(), output.resolve()
    if output == previous or previous in output.parents:
        raise ValueError('destination must be outside frozen input')
    before = {}
    for label in 'ABCD':
        base = previous / 'diagnostic' / label
        actual = inventory(base / 'source')
        expected = json.loads((base / 'source-inventory.json').read_text())
        if actual != expected:
            raise ValueError(f'frozen source mismatch: {label}')
        before[label] = {'source': actual, 'harness-source': inventory(base / 'harness-source')}
    for label in 'ABCD':
        for name in ('source', 'harness-source'):
            fingerprint = hashlib.sha256(json.dumps(before[label][name], sort_keys=True).encode()).hexdigest()
            if fingerprint != REVIEWED[label][name]:
                raise ValueError(f'unreviewed frozen input: {label}/{name}')
    if output.exists():
        raise FileExistsError(output)
    # Review all anchors before creating the exclusive destination.
    with tempfile.TemporaryDirectory(prefix='startup-anchor-review-') as temporary:
        for label in 'ABCD':
            base = Path(temporary) / label
            for name in ('source', 'harness-source'):
                shutil.copytree(previous / 'diagnostic' / label / name, base / name)
            overlay(base, output / 'trace.h')
    output.mkdir()  # Exclusive; never reuse a destination.
    header = output / 'trace.h'
    header.write_text(HEADER)
    shutil.copyfile(__file__, output / 'prepare.py')
    manifest = {'invocation': invocation, 'input': str(previous), 'before': before,
                'status': 'UNCOMPILED; no build, benchmark or new measurement authorized', 'outputs': {}}
    for label in 'ABCD':
        base = output / label
        base.mkdir()
        original = previous / 'diagnostic' / label
        for name in ('source', 'harness-source'):
            shutil.copytree(original / name, base / name)
        overlay(base, header)
        diff = []
        for name in ('source', 'harness-source'):
            for relative in before[label][name]:
                old, new = original / name / relative, base / name / relative
                if old.read_bytes() != new.read_bytes():
                    diff.extend(difflib.unified_diff(old.read_text().splitlines(True), new.read_text().splitlines(True),
                                                    fromfile=str(old), tofile=str(new)))
        (base / 'overlay.diff').write_text(''.join(diff))
        manifest['outputs'][label] = inventory(base)
    manifest['after'] = {label: {name: inventory(previous / 'diagnostic' / label / name)
                                for name in ('source', 'harness-source')} for label in 'ABCD'}
    if manifest['before'] != manifest['after']:
        raise RuntimeError('frozen inputs changed')
    manifest['header_sha256'] = legacy.digest(header)
    manifest['tool_sha256'] = legacy.digest(Path(__file__))
    manifest['dependency_tool_sha256'] = legacy.digest(Path(legacy.__file__))
    shutil.copyfile(legacy.__file__, output / 'prepare-preview-standby-diagnostic.py')
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    (output / 'README.md').write_text('# Private startup tracing preparation\n\nAll four overlays are uncompiled. D retains its frozen initial deferral. No execution is authorized. See manifest.json for exact invocation and input/output hashes, and each overlay.diff for review.\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('previous', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    prepare(args.previous, args.output, {'argv': sys.argv, 'cwd': str(Path.cwd())})
    print(args.output)


if __name__ == '__main__':
    main()
