#!/usr/bin/env python3
"""Verify frozen v3 inputs and prepare exclusive private cancellation overlays."""
import argparse
import difflib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('startup_smoke', ROOT / 'scripts/run-preview-startup-smoke.py')
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)
TEMPLATES = ROOT / 'tooling/preview-cancellation'


def tool_inputs():
    paths = list(TEMPLATES.glob('*')) + [ROOT / 'scripts' / name for name in (
        'prepare-preview-cancellation.py', 'build-preview-cancellation.py',
        'run-preview-cancellation.py', 'validate-preview-cancellation.py',
        'run-preview-startup-smoke.py', 'analyze-preview-startup.py',
        'manage-images-generations.py', 'measure-preview-reuse.py')]
    paths.append(ROOT / 'tests/test_preview_cancellation.py')
    return {str(path): smoke.digest(path) for path in paths if path.is_file()}



def replace(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise ValueError(f'anchor count {text.count(old)}: {path}: {old!r}')
    path.write_text(text.replace(old, new))


def overlay(base, header):
    source = base / 'source'
    for path in source.rglob('*.cpp'):
        text = path.read_text()
        if re.search(r'#include "[^"\n]*/trace.h"', text):
            path.write_text(re.sub(r'#include "[^"\n]*/trace.h"', '#include "'+str(header)+'"\n#include "'+str(header.with_name('diagnostic.h'))+'"', text))
    service = source / 'holonight-file-browser/src/preview/preview_service.cpp'
    replace(service, '  pending_job_ = false;\n  active_job_ = true;',
            '  CancellationDiagnostic::probe("submit", generation_, {{"path", path_}});\n  pending_job_ = false;\n  active_job_ = true;')
    # Observe existing request context, result identity and acceptance guards.
    replace(service, 'void PreviewService::applyResult(const PreviewResult& result) {',
            'void PreviewService::applyResult(const PreviewResult& result) {\n  CancellationDiagnostic::probe("application_attempt", result.generation, {{"current_selection", qint64(generation_)}, {"pixels", !result.image.isNull()}, {"final", result.final}, {"success", CancellationDiagnostic::successfulResult(result)}});')
    replace(service, '  if (result.final) {\n    timeout_timer_.stop();',
            '  CancellationDiagnostic::probe("accepted", result.generation, {{"pixels", !result.image.isNull()}, {"final", result.final}, {"success", CancellationDiagnostic::successfulResult(result)}});\n  if (result.final) {\n    timeout_timer_.stop();')
    replace(service, '        const auto publish = [this](const PreviewResult& result) {',
            '        const auto publish = [this](const PreviewResult& result) {\n          CancellationDiagnostic::probe("publication", result.generation, {{"pixels", !result.image.isNull()}, {"final", result.final}, {"success", CancellationDiagnostic::successfulResult(result)}});')
    replace(service, '  if (thread_.isRunning()) {\n    QMetaObject::invokeMethod(',
            '  CancellationDiagnostic::probe("destructor_cancel", 0, {{"cancelled", cancellation_ && cancellation_->load()}});\n  if (thread_.isRunning()) {\n    QMetaObject::invokeMethod(')
    pool = source / 'holonight-file-browser/src/preview/session_pool.cpp'
    replace(pool, '  state_->schedule();\n  state_->notifyReadiness();\n}\nvoid PreviewSessionPool::refresh()',
            '  state_->schedule();\n  if (state_->pending) CancellationDiagnostic::probe("pending");\n  state_->notifyReadiness();\n}\nvoid PreviewSessionPool::refresh()')
    replace(pool, '      slot.cancelled->store(true);\n    }\n    if (slot.phase == State::Phase::Ready)',
            '      slot.cancelled->store(true);\n      auto c = StandbyTrace::current; c.worker = slot.trace_worker; c.preparation = slot.trace_preparation;\n      StandbyTrace::Bind bind(c); CancellationDiagnostic::probe("preparation_cancel_set", 0, {{"cancelled", slot.cancelled->load()}});\n    }\n    if (slot.phase == State::Phase::Ready)')
    replace(pool, 'RuntimeStatus result, qint64 idle_memory, const std::shared_ptr<std::atomic_bool>& cancel) {',
            'RuntimeStatus result, qint64 idle_memory, const std::shared_ptr<std::atomic_bool>& cancel) {\n    CancellationDiagnostic::probe("terminal", 0, {{"cancelled", cancel->load()}, {"cleanup_ok", cleanup_status != RuntimeStatus::CleanupFailure}});')
    replace(pool, 'quint64 preparing_demand, qint64 idle_memory) {',
            'quint64 preparing_demand, qint64 idle_memory) {\n    CancellationDiagnostic::probe("preparation_terminal", 0, {{"cleanup_ok", prepared.runtime != RuntimeStatus::CleanupFailure}});')
    replace(pool, '    pending.reset();\n    for (auto& slot : workers)',
            '    if (pending) { StandbyTrace::Bind bind(pending->trace_context); CancellationDiagnostic::probe("pending_destroyed", 0, {{"cancelled", pending->cancelled->load()}}); }\n    pending.reset();\n    for (auto& slot : workers)')
    runtime = source / 'holonight-images/src/isolated/runtime.cpp'
    replace(runtime, '    check();\n    if (fileBytes(group + "/memory.max")',
            '    CancellationDiagnostic::preparation(cancelled);\n    check();\n    if (fileBytes(group + "/memory.max")')
    replace(runtime, '    if (process.write("G", 1) != 1)',
            '    CancellationDiagnostic::probe("gate_open");\n    if (process.write("G", 1) != 1)')
    replace(runtime, '    retired = true;\n    prepared = false;',
            '    CancellationDiagnostic::retirement();\n    CancellationDiagnostic::probe("retirement_entry");\n    retired = true;\n    prepared = false;')
    replace(runtime, '    result.elapsed = elapsed.elapsed();\n  }\n};',
            '    CancellationDiagnostic::probe("retirement_complete", 0, {{"verified", cleanup_verified && (!report || report->verified)}, {"launched", launched}});\n    result.elapsed = elapsed.elapsed();\n  }\n};')


def prepare(previous, fixtures, output):
    previous, fixtures, output = previous.resolve(), fixtures.resolve(), output.resolve()
    if output.exists() or previous == output or previous in output.parents:
        raise ValueError('exclusive destination required outside retained package')
    before = smoke.preflight(previous, fixtures)
    tools = tool_inputs()
    header = smoke.REVIEW / 'trace.h'
    with tempfile.TemporaryDirectory(prefix='cancellation-anchor-review-') as temporary:
        for label in 'CD':
            base = Path(temporary) / label
            shutil.copytree(previous / label / 'source', base / 'source')
            overlay(base, output / 'trace.h')
    output.mkdir()
    shutil.copyfile(header, output / 'trace.h')
    shutil.copyfile(TEMPLATES / 'diagnostic.h', output / 'diagnostic.h')
    manifest = {'input': str(previous), 'fixtures': str(fixtures), 'before': before, 'sources': {}, 'harness_sources': {}, 'tool_inputs': tools, 'private_inputs': {name: smoke.digest(output / name) for name in ('trace.h', 'diagnostic.h')}, 'commands': sys.argv}
    for label in 'CD':
        base = output / label
        shutil.copytree(previous / label / 'source', base / 'source')
        shutil.copytree(TEMPLATES, base / 'harness-source')
        overlay(base, output / 'trace.h')
        (base / 'harness-source/diagnostic.h').unlink()  # One shared diagnostic state definition.
        (base / 'harness-source/main.cpp').write_text((base / 'harness-source/main.cpp').read_text().replace('"diagnostic.h"', '"'+str(output / 'diagnostic.h')+'"'))
        diff = []
        for relative in smoke.inventory(previous / label / 'source'):
            old, new = previous / label / 'source' / relative, base / 'source' / relative
            if old.read_bytes() != new.read_bytes():
                diff.extend(difflib.unified_diff(old.read_text().splitlines(True), new.read_text().splitlines(True), fromfile=str(old), tofile=str(new)))
        (base / 'overlay.diff').write_text(''.join(diff))
        manifest['sources'][label] = smoke.inventory(base / 'source')
        manifest['harness_sources'][label] = smoke.inventory(base / 'harness-source')
    manifest['after'] = smoke.preflight(previous, fixtures)
    if manifest['after'] != before:
        raise ValueError('retained inputs changed')
    smoke.verify_hashes(ROOT, tools)
    smoke.write(output / 'preparation.json', manifest)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('previous', 'fixtures', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(prepare(args.previous, args.fixtures, args.output))


if __name__ == '__main__':
    main()
