#!/usr/bin/env python3
"""Prepare private, uncompiled A/B/C/D delivery probes without subprocesses."""
import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


g = module('delivery_gaps', ROOT / 'scripts/analyze-preview-delivery-gaps-v3.py')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(path):
    result = {}
    for p in sorted(path.rglob('*')):
        if p.is_symlink():
            raise ValueError('symlink in frozen tree: ' + str(p))
        if p.is_file():
            result[str(p.relative_to(path))] = digest(p)
    return result


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


HEADER = r'''
// Private supplemental probes. Zero identities are explicitly unavailable (JSON null).
#include <exception>
#include <string>
namespace DeliveryTrace {
inline std::atomic<unsigned long long> sequence{1};
inline unsigned long long identity() { return sequence.fetch_add(1); }
inline long long now() { timespec t{}; clock_gettime(CLOCK_MONOTONIC, &t); return static_cast<long long>(t.tv_sec)*1000000000LL+t.tv_nsec; }
inline std::string id(unsigned long long value) { return value ? std::to_string(value) : "null"; }
inline void event(const char* operation, const char* edge="point", unsigned long long span=0,
                  const char* outcome="unavailable", long long captured=0) {
  const auto c=StandbyTrace::current;
  char line[2048];
  int n=std::snprintf(line,sizeof(line),"DELIVERY {\"version\":4,\"ns\":%lld,\"pid\":%d,\"tid\":%ld,\"service\":%s,\"observation\":%s,\"job\":%s,\"worker\":%s,\"preparation\":%s,\"generation\":%s,\"session\":%s,\"transaction\":%s,\"publication\":%s,\"endpoint\":\"%s\",\"operation\":\"%s\",\"edge\":\"%s\",\"span\":%s,\"outcome\":\"%s\"}\n",
    captured ? captured : now(),getpid(),syscall(SYS_gettid),id(c.service).c_str(),id(c.observation).c_str(),id(c.job).c_str(),id(c.worker).c_str(),id(c.preparation).c_str(),id(c.delivery_generation).c_str(),id(c.delivery_session).c_str(),id(c.delivery_transaction).c_str(),id(c.delivery_publication).c_str(),c.delivery_endpoint,operation,edge,id(span).c_str(),outcome);
  if(n>0 && n<static_cast<int>(sizeof(line))) { auto ignored=write(2,line,n); (void)ignored; }
}
struct Scope {
  const char* operation; unsigned long long span=DeliveryTrace::identity();
  StandbyTrace::Context context=StandbyTrace::current;
  int exceptions=std::uncaught_exceptions(); const char* outcome="returned";
  explicit Scope(const char* op):operation(op) { event(operation,"begin",span); }
  ~Scope() { StandbyTrace::Bind bind(context); event(operation,"end",span,std::uncaught_exceptions()>exceptions ? "exception" : outcome); }
};
inline bool condition(const char* name, bool value) { event(name,"point",0,value ? "true" : "false"); return value; }
template<class F> bool boolean(const char* name, F operation) { Scope scope(name); const bool value=operation(); scope.outcome=value ? "success" : "failure"; return value; }
}
'''


def patch(base, header, variant):
    """Every replacement is exact and unique, independently checked for each variant."""
    anchors = []

    def edit(relative, old, new, operation):
        path = base / relative
        text = path.read_text()
        if text.count(old) != 1:
            raise ValueError(f'{variant}: missing/duplicate anchor {relative}: {operation} ({text.count(old)})')
        path.write_text(text.replace(old, new, 1))
        anchors.append(dict(file=relative, operation=operation, anchor=old, replacement=new))

    def add(relative, anchor, code, operation):
        edit(relative, anchor, anchor + '\n' + code, operation)

    images = 'source/holonight-images/src/isolated/'
    preview = 'source/holonight-file-browser/src/preview/'
    service = preview + 'preview_service.cpp'
    # Includes redirect only in files already using the frozen v3 header.
    for path in sorted(base.rglob('*.cpp')):
        text = path.read_text()
        matches = re.findall(r'#include "[^"\n]*/trace.h"', text)
        if matches:
            edit(str(path.relative_to(base)), matches[0], '#include "' + str(header) + '"', 'private_header')
    for relative in (images + 'client.cpp', preview + 'thumbnail_service.cpp', 'source/holonight-thumbnails/src/cache.cpp'):
        path = base / relative
        if str(header) not in path.read_text():
            original = path.read_text().splitlines()[0]
            edit(relative, original, '#include "' + str(header) + '"\n' + original, 'private_header')

    client = images + 'client.cpp'
    for signature in ('const SourceCoordinator& coordinate) const {',) + (() if variant == 'A' else ('\n                                                               const SourceCoordinator& coordinate) {',)):
        add(client, signature, '  StandbyTrace::current.delivery_transaction = DeliveryTrace::identity();\n  DeliveryTrace::Scope delivery_wrapper("transaction_wrapper");', 'transaction_wrapper')
    runtime = images + 'runtime.cpp'
    if variant != 'A':
        add(runtime, '  bool retired = false;', '  unsigned long long delivery_session = DeliveryTrace::identity();', 'session_identity')
        # This sets only diagnostic identities, never transaction_id/sequence on the wire.
        edit(runtime, '    auto reply = exchange(request, input, false);', '    StandbyTrace::current.delivery_session = delivery_session;\n    auto reply = exchange(request, input, false);', 'session_binding')
        # Bracket the whole existing completion branch without moving its return.
        edit(runtime, '    if (session) {\n      send(frame(QJsonObject{\n',
             '    if (session) {\n      DeliveryTrace::Scope delivery_completion("reusable_completion_ack");\n      send(frame(QJsonObject{\n', 'reusable_completion_ack')
        add(runtime, '      ++transaction_id;', '      delivery_completion.outcome = "acknowledged";', 'completion_validated')
        edit(runtime, '  void retire() {\n  StandbyTrace::Scope trace("cleanup", this, -1);',
             '  void retire() {\n  StandbyTrace::current.delivery_session = delivery_session;\n  DeliveryTrace::Scope delivery_retire("retirement_call");\n  StandbyTrace::Scope trace("cleanup", this, -1);', 'retirement_call')
        add(runtime, '    if (retired) {', '      delivery_retire.outcome = "already_retired";', 'repeated_retirement')
        add(runtime, '    retired = true;', '    delivery_retire.outcome = "effective_retirement";', 'effective_retirement')
    else:
        edit(runtime, '    auto reply = exchange(request, input, false);', '    StandbyTrace::current.delivery_session = DeliveryTrace::identity();\n    auto reply = exchange(request, input, false);', 'oneshot_session')
    edit(runtime, '    if (process.write("A", 1) != 1) {',
         '    { DeliveryTrace::Scope delivery_ack("oneshot_ack");\n    if (process.write("A", 1) != 1) {', 'oneshot_ack_begin')
    edit(runtime, '    process.closeWriteChannel();\n    while (process.state() != QProcess::NotRunning) {',
         '    delivery_ack.outcome = "sent"; }\n    process.closeWriteChannel();\n    { DeliveryTrace::Scope delivery_exit("helper_exit");\n    while (process.state() != QProcess::NotRunning) {', 'helper_exit_begin')
    edit(runtime, '      throw ProtocolError("helper failed or trailing response");\n    }\n    check();',
         '      throw ProtocolError("helper failed or trailing response");\n    }\n    delivery_exit.outcome = "validated_exit"; }\n    check();', 'helper_exit_end')
    indent = '    ' if variant == 'A' else '      '
    edit(runtime, indent + 'report = cleanup(operations, unit, group);',
         indent + 'DeliveryTrace::Scope delivery_cleanup("effective_cleanup");\n' + indent + 'report = cleanup(operations, unit, group);\n' + indent + 'delivery_cleanup.outcome = report->verified ? "verified" : "unverified";', 'effective_cleanup')
    # Mark absence using the already evaluated launched branch.
    old = indent + 'delivery_cleanup.outcome = report->verified ? "verified" : "unverified";\n' + indent[:-2] + '}'
    edit(runtime, old, old + ' else { DeliveryTrace::event("effective_cleanup", "point", 0, "not_launched"); }', 'cleanup_not_launched')

    # Generation exists before every demand worker handoff, including deferred jobs.
    add(service, '  demand_context.role = "demand";', '  demand_context.delivery_generation = generation_;', 'generation')
    old = '''        const auto publish = [this](const PreviewResult& result) {
          QMetaObject::invokeMethod(this, [this, result, trace_context = StandbyTrace::current] {
          StandbyTrace::Bind trace_bind(trace_context); applyResult(result); }, Qt::QueuedConnection);
        };'''
    new = '''        const auto publish = [this](const PreviewResult& result) {
          auto delivery_context = StandbyTrace::current;
          delivery_context.delivery_publication = DeliveryTrace::identity();
          delivery_context.delivery_generation = result.generation;
          delivery_context.delivery_endpoint = result.final ? "final_result" : "pixel_result";
          StandbyTrace::Bind delivery_bind(delivery_context);
          DeliveryTrace::Scope delivery_enqueue("enqueue_call");
          QMetaObject::invokeMethod(this, [this, result, trace_context = StandbyTrace::current] {
          StandbyTrace::Bind trace_bind(trace_context);
          DeliveryTrace::Scope delivery_callback("callback_execution");
          applyResult(result); }, Qt::QueuedConnection);
        };'''
    edit(service, old, new, 'publication_handoff')
    add(service, 'void PreviewService::applyResult(const PreviewResult& result) {', '  DeliveryTrace::Scope delivery_apply("apply_result");', 'apply_result')
    add(service, '       result.raster_outcome == HolonightImages::Outcome::Cancelled)) {', '    DeliveryTrace::event("result_decision", "point", 0, "cancelled");', 'cancelled_result')
    add(service, '  if (result.generation != generation_) {', '    DeliveryTrace::event("result_decision", "point", 0, "stale");', 'stale_result')
    edit(service, '  if (timed_out_) {\n    // A slow-but-eventually-successful', '  if (timed_out_) {\n    DeliveryTrace::event("result_decision", "point", 0, "timed_out");\n    // A slow-but-eventually-successful', 'timed_out_result')
    edit(service, '  if (result.final) {\n    timeout_timer_.stop();\n', '  DeliveryTrace::event("result_decision", "point", 0, "accepted");\n  if (result.final) {\n    timeout_timer_.stop();\n', 'accepted_result')
    edit(service, 'void PreviewService::notifyChanged() {\n  emit changed();', 'void PreviewService::notifyChanged() {\n  { DeliveryTrace::Scope delivery_changed("changed_emission");\n    emit changed();\n  }', 'changed_emission')
    # Preserve short circuit order, all cancellation loads and unchangedSource calls.
    for operation, old, new in (
        ('storage_decision', 'decodedSource && tier && result.raster_outcome == HolonightImages::Outcome::Success &&\n      unchangedSource(file, identity)',
         'DeliveryTrace::condition("store.decoded_source", decodedSource) && DeliveryTrace::condition("store.tier", bool(tier)) && DeliveryTrace::condition("store.success", result.raster_outcome == HolonightImages::Outcome::Success) &&\n      DeliveryTrace::condition("store.unchanged", unchangedSource(file, identity))'),
        ('memory_decision', '!cancel->load() && result.raster_outcome == HolonightImages::Outcome::Success &&\n      unchangedSource(file, identity) && !cancel->load()',
         'DeliveryTrace::condition("memory.not_cancelled_before", !cancel->load()) && DeliveryTrace::condition("memory.success", result.raster_outcome == HolonightImages::Outcome::Success) &&\n      DeliveryTrace::condition("memory.unchanged", unchangedSource(file, identity)) && DeliveryTrace::condition("memory.not_cancelled_after", !cancel->load())'),
    ):
        edit(service, old, new, operation)
    edit(service, '    ThumbnailService::storeRaster(file, path, identity, *tier, needed, result.image, *cancel, stage, nativePath);\n  }',
         '    DeliveryTrace::Scope delivery_store("store_raster");\n    ThumbnailService::storeRaster(file, path, identity, *tier, needed, result.image, *cancel, stage, nativePath);\n  } else { DeliveryTrace::event("store_raster", "point", 0, "skipped"); }', 'store_raster')
    edit(service, 'result.mime_type == QLatin1String("image/jpeg") || result.mime_type == QLatin1String("image/png")',
         'DeliveryTrace::condition("format.jpeg", result.mime_type == QLatin1String("image/jpeg")) || DeliveryTrace::condition("format.png", result.mime_type == QLatin1String("image/png"))', 'format_decision')
    edit(service, '    result.exif = ExifReader::format(inspection.metadata);\n  }',
         '    DeliveryTrace::Scope delivery_format("metadata_format");\n    result.exif = ExifReader::format(inspection.metadata);\n  } else { DeliveryTrace::event("metadata_format", "point", 0, "skipped"); }', 'metadata_format')
    edit(service, '    cache.insert(identity, image,\n                 PreviewWorkerCache::RasterFacts{.source_size = result.source_pixel_size, .exif = result.exif});\n  }',
         '    DeliveryTrace::Scope delivery_memory("memory_insert");\n    cache.insert(identity, image,\n                 PreviewWorkerCache::RasterFacts{.source_size = result.source_pixel_size, .exif = result.exif});\n  } else { DeliveryTrace::event("memory_insert", "point", 0, "skipped"); }', 'memory_insert')
    # Raster function exits get a stable checkpoint reason without extra predicate evaluation.
    path = base / service
    text = path.read_text()
    start, stop = text.index('PreviewResult decodeImage('), text.index('PreviewResult decodeSvg(')
    section = text[start:stop]
    for index, match in reversed(list(enumerate(re.finditer(r'(?m)^(\s*)return result;', section)))):
        pos = match.start()
        section = section[:pos] + match.group(1) + f'DeliveryTrace::event("raster_exit", "point", 0, "checkpoint_{index}");\n' + section[pos:]
    edit(service, text[start:stop], section, 'raster_exit_checkpoints')

    edit(preview + 'thumbnail_service.cpp', '                 const QByteArray& nativePath) {\n  HolonightThumbnails::store',
         '                 const QByteArray& nativePath) {\n  DeliveryTrace::Scope delivery_delegate("store_raster_delegate");\n  HolonightThumbnails::store', 'store_raster_delegate')
    cache = 'source/holonight-thumbnails/src/cache.cpp'
    add(cache, 'bool store(const Request& request, const QImage& image, const std::atomic_bool& cancelled, const StageCallback& stage) {', '  DeliveryTrace::Scope delivery_store("thumbnail_store");', 'thumbnail_store')
    edit(cache, 'tagged.save(&file, "PNG")', 'DeliveryTrace::boolean("png_serialization", [&] { return tagged.save(&file, "PNG"); })', 'png_serialization')
    edit(cache, 'if (!file.commit()) {', 'if (!DeliveryTrace::boolean("storage_commit", [&] { return file.commit(); })) {', 'storage_commit')
    text = (base / cache).read_text()
    start = text.index('bool store(')
    section = text[start:]
    for expression, name in (('cancelled.load()', 'cancelled'), ('!validRequest(request)', 'invalid_request'), ('image.isNull()', 'null_image'),
                             ('!ensureDirectory(QFileInfo(path).absolutePath())', 'directory_failure')):
        section = section.replace(expression, 'DeliveryTrace::condition("storage.' + name + '", ' + expression + ')')
    count = 0
    for match in reversed(list(re.finditer(r'(?m)^(\s*)return (false|true);', section))):
        count += 1
        outcome = 'success' if match.group(2) == 'true' else f'failure_checkpoint_{count}'
        section = section[:match.start()] + match.group(1) + f'delivery_store.outcome = "{outcome}";\n' + section[match.start():]
    edit(cache, text[start:], section, 'storage_exits')
    harness = 'harness-source/reuse.cpp'
    add(harness, 'const auto connection = QObject::connect(service.get(), &PreviewService::changed, &app, [&] {', '      const auto delivery_entry = DeliveryTrace::now();', 'harness_entry_capture')
    add(harness, '      const auto latency = (clock.nsecsElapsed() - selected_at) / 1000000.0;', '      const auto delivery_captured = DeliveryTrace::now();\n      DeliveryTrace::event("harness_entry", "point", 0, "captured", delivery_entry);\n      DeliveryTrace::Scope delivery_harness("harness_execution");\n      DeliveryTrace::event("latency_capture", "point", 0, "captured", delivery_captured);', 'harness_post_latency')
    for endpoint in ('pixels', 'metadata'):
        add(harness, f'        StandbyTrace::event("{endpoint}", "point", service.get());', f'        DeliveryTrace::event("endpoint_{endpoint}", "point", 0, "satisfied");', 'endpoint_' + endpoint)
    return anchors


def prepare(root, prior, output):
    root, prior, output = (p.resolve() for p in (root, prior, output))
    if ROOT / 'build' not in output.parents or any(p == output or p in output.parents or output in p.parents for p in (root, prior)):
        raise ValueError('fresh output must be under ignored build/ and disjoint from inputs')
    if '/build/' not in (ROOT / '.gitignore').read_text().splitlines():
        raise ValueError('build/ is not ignored')
    output.mkdir()
    before, issues, outputs = {}, [], {}

    def read(path, expected=None):
        path = path.resolve()
        actual = digest(path)
        before[str(path)] = actual
        if expected is not None and actual != expected:
            raise ValueError('integrity mismatch: ' + str(path))
        return path.read_text()

    def load(path, expected=None):
        return json.loads(read(path, expected))

    try:
        for path in [Path(__file__), ROOT / 'scripts/analyze-preview-delivery-tracing.py',
                     ROOT / 'tests/test_preview_delivery_tracing.py', ROOT / 'docs/initiatives/delivery-tracing-v4.md']:
            read(path)
        integrity = load(prior / 'input-integrity.json')
        if not integrity['unchanged'] or integrity['before'] != integrity['after']:
            raise ValueError('prior input integrity is blocked')
        for name, expected in integrity['before'].items():
            read(Path(name), expected)
        if load(prior / 'assessment.json')['status'] != 'complete':
            raise ValueError('delivery-gap analysis is blocked')
        # Historical validation is offline Python only. Reconcile the completed analysis.
        startup = load(prior / 'revalidated-startup/input-integrity.json')
        for name, expected in startup['before'].items():
            read(Path(name), expected)
        if g.analyze(root, prior / 'revalidated-startup', output / 'revalidated-gaps'):
            raise ValueError('historical revalidation failed')
        for name in ('inventory', 'intervals', 'summary', 'source-path-map', 'selected-examples', 'issues', 'assessment'):
            if load(prior / (name + '.json')) != load(output / 'revalidated-gaps' / (name + '.json')):
                raise ValueError('analysis reconciliation mismatch: ' + name)
        seal = load(root / 'seal.json')
        prep = load(root / 'preparation.json', seal['preparation.json'])
        for name, expected in prep['tools'].items():
            read(Path(name), expected)
        trees = {}
        for variant in 'ABCD':
            trees[variant] = {}
            for category in ('source', 'harness-source'):
                tree = root / (variant + 'T') / category
                actual = inventory(tree)
                if actual != prep['pairs'][variant + 'T'][category]:
                    raise ValueError('source inventory mismatch: ' + str(tree))
                trees[variant][category] = actual
                for relative, expected in actual.items():
                    read(tree / relative, expected)
        header = read(root / 'trace.h', seal['trace.h'])
        old = '  const char* role="setup";'
        if header.count(old) != 1:
            raise ValueError('missing/duplicate context anchor')
        header = header.replace(old, old + '\n  unsigned long long delivery_generation=0, delivery_session=0, delivery_transaction=0, delivery_publication=0;\n  const char* delivery_endpoint="unavailable";') + HEADER
        # Review every variant on temporary copies before emitting any prepared source tree.
        with tempfile.TemporaryDirectory(prefix='delivery-anchor-review-') as temporary:
            reviews = {}
            for variant in 'ABCD':
                base = Path(temporary) / variant
                for category in ('source', 'harness-source'):
                    shutil.copytree(root / (variant + 'T') / category, base / category)
                reviews[variant] = patch(base, output / 'trace.h', variant)
                write(output / 'anchor-review.json', reviews)
            (output / 'trace.h').write_text(header)
            for variant in 'ABCD':
                base = output / variant
                shutil.copytree(Path(temporary) / variant, base)
                diff = []
                for category, files in trees[variant].items():
                    for relative in files:
                        old, new = root / (variant + 'T') / category / relative, base / category / relative
                        if old.read_bytes() != new.read_bytes():
                            diff.extend(difflib.unified_diff(old.read_text().splitlines(True), new.read_text().splitlines(True), fromfile=str(old), tofile=str(new)))
                (base / 'overlay.diff').write_text(''.join(diff))
                maps = []
                for category in ('source', 'harness-source'):
                    for path in sorted((base / category).rglob('*.cpp')):
                        for number, line in enumerate(path.read_text().splitlines(), 1):
                            if 'DeliveryTrace::' in line or 'delivery_' in line:
                                maps.append(dict(file=str(path), line=number, text=line, sha256=digest(path)))
                write(base / 'probe-to-source.json', dict(variant=variant, anchors=reviews[variant], probes=maps))
                write(base / 'source-inventory.json', {category: inventory(base / category) for category in ('source', 'harness-source')})
                outputs[variant] = inventory(base)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        issues.append(str(error))
    after = {name: digest(Path(name)) if Path(name).is_file() else None for name in before}
    if before != after:
        issues.append('consumed inputs changed')
    manifest = dict(status='blocked' if issues else 'prepared', warning='UNCOMPILED — no runtime validation or measurements',
                    inputs=dict(overhead=str(root), delivery_gaps=str(prior)), issues=issues, outputs=outputs,
                    before=before, after=after, unchanged=before == after, argv=sys.argv)
    if (output / 'trace.h').exists():
        manifest['header_sha256'] = digest(output / 'trace.h')
    write(output / 'manifest.json', manifest)
    (output / 'README.md').write_text('# Private delivery tracing\n\n**UNCOMPILED — no runtime validation or measurements**\n\nStatus: ' + manifest['status'] + '. See [manifest](manifest.json), variant overlay.diff, source-inventory.json and probe-to-source.json.\n\nOnly frozen traced sources and harness trees were copied. D retains initial deferral. Diagnostic timestamp capture and logging add unmeasured overhead. Original v3 records remain separate. No compilability, overhead or gap-attribution claim; C qualification and D pilot remain failed. Native validation and any experiment require a separate plan.\n\nSchema: [delivery-tracing-v4.md](' + os.path.relpath(ROOT / 'docs/initiatives/delivery-tracing-v4.md', output) + ').\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('overhead', 'analysis', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    result = prepare(args.overhead, args.analysis, args.output)
    print(result['status'], args.output)
    return int(result['status'] == 'blocked')


if __name__ == '__main__':
    sys.exit(main())
