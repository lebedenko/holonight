#!/usr/bin/env python3
"""Prepare private cache publication sources only; no build or execution interface."""
import argparse
import difflib
import importlib.util
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('cache_evidence', Path(__file__).with_name('preview-cache-publication-evidence.py'))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
h = e.h

HELPER = '''#include <QJsonDocument>
#include <QJsonObject>
#include <QThread>
#include <QUuid>
#include <QDebug>
#include <time.h>

static void cachePublicationEvent(QJsonObject context, const char* event) {
  struct timespec now{};
  clock_gettime(CLOCK_MONOTONIC, &now);
  context["event"] = QString::fromLatin1(event);
  context["ns"] = QString::number(qint64(now.tv_sec) * 1000000000 + now.tv_nsec);
  qInfo().noquote() << "CACHE_PUBLICATION" << QJsonDocument(context).toJson(QJsonDocument::Compact);
}

'''


def replace(text, old, new, anchors):
    h.require(text.count(old) == 1, 'literal anchor mismatch: ' + old[:100])
    anchors.append(dict(before=old, after=new))
    return text.replace(old, new, 1)


def transform(text, name, early):
    anchors = []
    def edit(old, new):
        nonlocal text
        text = replace(text, old, new, anchors)
    if name == e.RUNTIME:
        edit('#include "runtime.h"', '#include "runtime.h"\n#include <QJsonObject>')
        edit('  int transaction_id = 1;', '  const QString cachePreparation = QUuid::createUuid().toString();\n  int transaction_id = 1;')
        edit('    int sequence = 0;', '''    auto cacheContext = QThread::currentThread()->property("cachePublication").toJsonObject();
    cacheContext["preparation"] = cachePreparation;
    cacheContext["transaction"] = QString::number(transaction_id);
    QThread::currentThread()->setProperty("cachePublication", cacheContext);
    int sequence = 0;''')
    elif name == e.SERVICE:
        edit('#include "session_pool.h"', '#include "session_pool.h"\n' + HELPER)
        edit('struct PreviewResult {', 'struct PreviewResult {\n  QJsonObject cacheContext;')
        edit('  worker_->moveToThread(&thread_);', '  setProperty("cacheService", QUuid::createUuid().toString());\n  worker_->moveToThread(&thread_);')
        edit('  active_job_ = true;\n  const auto generation = generation_;', '''  active_job_ = true;
  const auto cacheContext = QJsonObject{{"invocation", qEnvironmentVariable("HOLONIGHT_CACHE_INVOCATION")},
      {"service", property("cacheService").toString()}, {"request", QUuid::createUuid().toString()}};
  const auto generation = generation_;''')
        edit('[this, path, nativePath, generation, cancel, size, beforeDispatch, beforeFull, stage, options, memoryCheckpoint]', '[this, path, nativePath, generation, cancel, size, beforeDispatch, beforeFull, stage, options, memoryCheckpoint, cacheContext]')
        edit('options, false, memoryCheckpoint, defer);', 'options, false, memoryCheckpoint, defer, cacheContext);')
        edit('const std::function<bool(QFile&, const QString&, const PreviewResult&)>& defer = {}) {\n  PreviewResult result;', 'const std::function<bool(QFile&, const QString&, const PreviewResult&)>& defer = {},\n                            QJsonObject cacheContext = {}) {\n  PreviewResult result;\n  result.cacheContext = cacheContext;')
        edit('  const auto reply = [&]()', '''  result.cacheContext["source"] = identity;
  result.cacheContext["width"] = requestedSize.width();
  result.cacheContext["height"] = requestedSize.height();
  result.cacheContext["generation"] = QString::number(result.generation);
  result.cacheContext["worker"] = QUuid::createUuid().toString();
  QThread::currentThread()->setProperty("cachePublication", result.cacheContext);
  const auto reply = [&]()''')
        edit('  result.runtime = reply.runtime;', '''  result.cacheContext = QThread::currentThread()->property("cachePublication").toJsonObject();
  result.cacheContext["original_decode"] = decodedSource;
  result.cacheContext["tier"] = tier ? static_cast<int>(*tier) : 0;
  result.cacheContext["outcome"] = reply.result ? static_cast<int>(reply.result->outcome) : -1;
  result.runtime = reply.runtime;''')
        edit('  if (decodedSource && tier && result.raster_outcome', '  bool cachePublished = false;\n  if (decodedSource && tier && result.raster_outcome')
        store = '    ThumbnailService::storeRaster(file, path, identity, *tier, needed, result.image, *cancel, stage, nativePath);'
        before = '''    cachePublicationEvent(result.cacheContext, "eligible");
'''
        if early:
            before += '''    auto progressive = result;
    progressive.final = false;
    if (cancel->load()) {
      return result;
    }
    cachePublicationEvent(progressive.cacheContext, "enqueue");
    publish(progressive);
    cachePublished = true;
'''
        edit(store, before + '    cachePublicationEvent(result.cacheContext, "store_entry");\n' + store + '\n    cachePublicationEvent(result.cacheContext, "store_return");')
        edit('  publish(result);\n  result.final = true;\n  result.image = {};  // EXIF', '''  if (!cachePublished) {
    cachePublicationEvent(result.cacheContext, "enqueue");
    publish(result);
  }
  result.final = true;
  result.image = {};  // EXIF''')
        edit('    display_image_ = result.image;', '    display_image_ = result.image;\n    cachePublicationEvent(result.cacheContext, "accepted");')
        edit('  notifyChanged();\n  if (result.final && mime_type_', '''  QThread::currentThread()->setProperty("cachePublicationDelivery", result.cacheContext);
  if (result.final) {
    cachePublicationEvent(result.cacheContext, "final");
  }
  notifyChanged();
  if (result.final && mime_type_''')
    elif name == 'reuse.cpp':
        text = HELPER + text
        anchors.append(dict(before='', after=HELPER))
        edit('      if (adequate && !pixel_delivered) {', '''      if (adequate && !pixel_delivered) {
        cachePublicationEvent(QThread::currentThread()->property("cachePublicationDelivery").toJsonObject(), "adequate");''')
    return text, anchors


def prepare(output):
    # A fresh direct build child cannot mutate a nested retained evidence package.
    h.require(output.parent == e.ROOT / 'build' and output.name.startswith('preview-cache-publication-'),
              'destination must be a fresh preview-cache-publication build child')
    h.fresh(output, [e.Q, e.ROOT / 'scripts', e.ROOT / 'docs', e.ROOT / 'tests'])
    assessment = dict(status='blocked', native_correctness='unvalidated', execution_capability='unvalidated',
                      decision='Evidence insufficient', executed_commands=[])
    inputs, tools = None, None
    integrity = dict(inputs_unchanged=False, tools_unchanged=False)
    try:
        tools = e.snapshots()
        (output / 'tools').mkdir()
        for path in tools:
            shutil.copyfile(path, output / 'tools' / Path(path).name)
        h.write(output / 'tools.json', tools)
        inputs = e.retained()
        h.require(all(not output.is_relative_to(Path(p)) and not Path(p).is_relative_to(output)
                      for p in inputs['inventories']), 'destination overlaps retained evidence')
        h.write(output / 'inputs.json', inputs)
        h.write(output / 'protocol.json', e.protocol())
        shutil.copyfile(inputs['fixture']['path'], output / '3200x2400.png')
        changes = {}
        for arm in e.ARMS:
            for group, source, inventory in [('source', e.Q / 'C/source', inputs['source']),
                                             ('harness-source', e.Q / 'harness-source', inputs['harness'])]:
                for name in inventory:
                    target = output / arm / group / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    original = (source / name).read_bytes()
                    if name in (e.SERVICE, e.RUNTIME) or (group == 'harness-source' and name == 'reuse.cpp'):
                        changed, anchors = transform(original.decode(), name, arm == 'early')
                        target.write_text(changed)
                        key = arm + '/' + group + '/' + name
                        changes[key] = anchors
                        (output / (arm + '-' + Path(name).name + '.diff')).write_text(''.join(
                            difflib.unified_diff(original.decode().splitlines(True), changed.splitlines(True),
                                                 fromfile='frozen/' + name, tofile=key)))
                    else:
                        target.write_bytes(original)
            h.write(output / (arm + '-inventory.json'), h.inventory(output / arm))
        h.write(output / 'anchors.json', changes)
        h.require(h.recheck(inputs['inventories'], inputs['files']) and e.snapshots() == tools, 'input drift after preparation')
        assessment['status'] = 'prepared'
    except (OSError, ValueError, KeyError, TypeError) as error:
        assessment['failure'] = str(error)
    # Recheck even after a blocked transformation; never repair an input discrepancy.
    try:
        integrity['inputs_unchanged'] = inputs is not None and h.recheck(inputs['inventories'], inputs['files'])
        integrity['tools_unchanged'] = tools is not None and e.snapshots() == tools
    except (OSError, ValueError, KeyError, TypeError) as error:
        integrity['failure'] = str(error)
    if not all(integrity.get(k) is True for k in ('inputs_unchanged', 'tools_unchanged')):
        assessment.update(status='blocked', failure=assessment.get('failure', 'post-preparation input drift'))
    h.write(output / 'integrity.json', integrity)
    h.write(output / 'assessment.json', assessment)
    (output / 'REPORT.md').write_text('# Cache publication diagnostic\n\n' + assessment['status'] +
        '; native correctness and execution capability unvalidated.\n\nNo build, staging, workload or recording executed. Overall candidate selection remains Evidence insufficient; streaming and validation reuse Deferred; qualification 78/80 unchanged.\n')
    h.write(output / 'seal.json', h.inventory(output))
    return assessment


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output.absolute())
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'prepared')
