#!/usr/bin/env python3
"""Independent offline reconstruction. Never imports the preparer or its transformations."""
import argparse
import difflib
import importlib.util
import math
from pathlib import Path
import sys
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('cache_offline_evidence', Path(__file__).with_name('preview-cache-publication-evidence.py'))
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
h = e.h
# Independently fixed literal allowlist; reverse each edit and compare complete original bytes.
EDITS = {'control/holonight-file-browser/src/preview/preview_service.cpp': [{'after': '#include "session_pool.h"\n'
                                                                              '#include <QJsonDocument>\n'
                                                                              '#include <QJsonObject>\n'
                                                                              '#include <QThread>\n'
                                                                              '#include <QUuid>\n'
                                                                              '#include <QDebug>\n'
                                                                              '#include <time.h>\n'
                                                                              '\n'
                                                                              'static void '
                                                                              'cachePublicationEvent(QJsonObject '
                                                                              'context, const char* event) '
                                                                              '{\n'
                                                                              '  struct timespec now{};\n'
                                                                              '  '
                                                                              'clock_gettime(CLOCK_MONOTONIC, '
                                                                              '&now);\n'
                                                                              '  context["event"] = '
                                                                              'QString::fromLatin1(event);\n'
                                                                              '  context["ns"] = '
                                                                              'QString::number(qint64(now.tv_sec) '
                                                                              '* 1000000000 + now.tv_nsec);\n'
                                                                              '  qInfo().noquote() << '
                                                                              '"CACHE_PUBLICATION" << '
                                                                              'QJsonDocument(context).toJson(QJsonDocument::Compact);\n'
                                                                              '}\n'
                                                                              '\n',
                                                                     'before': '#include "session_pool.h"'},
                                                                    {'after': 'struct PreviewResult {\n'
                                                                              '  QJsonObject cacheContext;',
                                                                     'before': 'struct PreviewResult {'},
                                                                    {'after': '  setProperty("cacheService", '
                                                                              'QUuid::createUuid().toString());\n'
                                                                              '  '
                                                                              'worker_->moveToThread(&thread_);',
                                                                     'before': '  '
                                                                               'worker_->moveToThread(&thread_);'},
                                                                    {'after': '  active_job_ = true;\n'
                                                                              '  const auto cacheContext = '
                                                                              'QJsonObject{{"invocation", '
                                                                              'qEnvironmentVariable("HOLONIGHT_CACHE_INVOCATION")},\n'
                                                                              '      {"service", '
                                                                              'property("cacheService").toString()}, '
                                                                              '{"request", '
                                                                              'QUuid::createUuid().toString()}};\n'
                                                                              '  const auto generation = '
                                                                              'generation_;',
                                                                     'before': '  active_job_ = true;\n'
                                                                               '  const auto generation = '
                                                                               'generation_;'},
                                                                    {'after': '[this, path, nativePath, '
                                                                              'generation, cancel, size, '
                                                                              'beforeDispatch, beforeFull, '
                                                                              'stage, options, '
                                                                              'memoryCheckpoint, '
                                                                              'cacheContext]',
                                                                     'before': '[this, path, nativePath, '
                                                                               'generation, cancel, size, '
                                                                               'beforeDispatch, beforeFull, '
                                                                               'stage, options, '
                                                                               'memoryCheckpoint]'},
                                                                    {'after': 'options, false, '
                                                                              'memoryCheckpoint, defer, '
                                                                              'cacheContext);',
                                                                     'before': 'options, false, '
                                                                               'memoryCheckpoint, defer);'},
                                                                    {'after': 'const '
                                                                              'std::function<bool(QFile&, '
                                                                              'const QString&, const '
                                                                              'PreviewResult&)>& defer = '
                                                                              '{},\n'
                                                                              '                            '
                                                                              'QJsonObject cacheContext = '
                                                                              '{}) {\n'
                                                                              '  PreviewResult result;\n'
                                                                              '  result.cacheContext = '
                                                                              'cacheContext;',
                                                                     'before': 'const '
                                                                               'std::function<bool(QFile&, '
                                                                               'const QString&, const '
                                                                               'PreviewResult&)>& defer = '
                                                                               '{}) {\n'
                                                                               '  PreviewResult result;'},
                                                                    {'after': '  '
                                                                              'result.cacheContext["source"] '
                                                                              '= identity;\n'
                                                                              '  '
                                                                              'result.cacheContext["width"] '
                                                                              '= requestedSize.width();\n'
                                                                              '  '
                                                                              'result.cacheContext["height"] '
                                                                              '= requestedSize.height();\n'
                                                                              '  '
                                                                              'result.cacheContext["generation"] '
                                                                              '= '
                                                                              'QString::number(result.generation);\n'
                                                                              '  '
                                                                              'result.cacheContext["worker"] '
                                                                              '= '
                                                                              'QUuid::createUuid().toString();\n'
                                                                              '  '
                                                                              'QThread::currentThread()->setProperty("cachePublication", '
                                                                              'result.cacheContext);\n'
                                                                              '  const auto reply = [&]()',
                                                                     'before': '  const auto reply = [&]()'},
                                                                    {'after': '  result.cacheContext = '
                                                                              'QThread::currentThread()->property("cachePublication").toJsonObject();\n'
                                                                              '  '
                                                                              'result.cacheContext["original_decode"] '
                                                                              '= decodedSource;\n'
                                                                              '  result.cacheContext["tier"] '
                                                                              '= tier ? '
                                                                              'static_cast<int>(*tier) : 0;\n'
                                                                              '  '
                                                                              'result.cacheContext["outcome"] '
                                                                              '= reply.result ? '
                                                                              'static_cast<int>(reply.result->outcome) '
                                                                              ': -1;\n'
                                                                              '  result.runtime = '
                                                                              'reply.runtime;',
                                                                     'before': '  result.runtime = '
                                                                               'reply.runtime;'},
                                                                    {'after': '  bool cachePublished = '
                                                                              'false;\n'
                                                                              '  if (decodedSource && tier '
                                                                              '&& result.raster_outcome',
                                                                     'before': '  if (decodedSource && tier '
                                                                               '&& result.raster_outcome'},
                                                                    {'after': '    '
                                                                              'cachePublicationEvent(result.cacheContext, '
                                                                              '"eligible");\n'
                                                                              '    '
                                                                              'cachePublicationEvent(result.cacheContext, '
                                                                              '"store_entry");\n'
                                                                              '    '
                                                                              'ThumbnailService::storeRaster(file, '
                                                                              'path, identity, *tier, '
                                                                              'needed, result.image, '
                                                                              '*cancel, stage, nativePath);\n'
                                                                              '    '
                                                                              'cachePublicationEvent(result.cacheContext, '
                                                                              '"store_return");',
                                                                     'before': '    '
                                                                               'ThumbnailService::storeRaster(file, '
                                                                               'path, identity, *tier, '
                                                                               'needed, result.image, '
                                                                               '*cancel, stage, '
                                                                               'nativePath);'},
                                                                    {'after': '  if (!cachePublished) {\n'
                                                                              '    '
                                                                              'cachePublicationEvent(result.cacheContext, '
                                                                              '"enqueue");\n'
                                                                              '    publish(result);\n'
                                                                              '  }\n'
                                                                              '  result.final = true;\n'
                                                                              '  result.image = {};  // EXIF',
                                                                     'before': '  publish(result);\n'
                                                                               '  result.final = true;\n'
                                                                               '  result.image = {};  // '
                                                                               'EXIF'},
                                                                    {'after': '    display_image_ = '
                                                                              'result.image;\n'
                                                                              '    '
                                                                              'cachePublicationEvent(result.cacheContext, '
                                                                              '"accepted");',
                                                                     'before': '    display_image_ = '
                                                                               'result.image;'},
                                                                    {'after': '  '
                                                                              'QThread::currentThread()->setProperty("cachePublicationDelivery", '
                                                                              'result.cacheContext);\n'
                                                                              '  if (result.final) {\n'
                                                                              '    '
                                                                              'cachePublicationEvent(result.cacheContext, '
                                                                              '"final");\n'
                                                                              '  }\n'
                                                                              '  notifyChanged();\n'
                                                                              '  if (result.final && '
                                                                              'mime_type_',
                                                                     'before': '  notifyChanged();\n'
                                                                               '  if (result.final && '
                                                                               'mime_type_'}],
 'control/holonight-images/src/isolated/runtime.cpp': [{'after': '#include "runtime.h"\n'
                                                                 '#include <QJsonObject>',
                                                        'before': '#include "runtime.h"'},
                                                       {'after': '  const QString cachePreparation = '
                                                                 'QUuid::createUuid().toString();\n'
                                                                 '  int transaction_id = 1;',
                                                        'before': '  int transaction_id = 1;'},
                                                       {'after': '    auto cacheContext = '
                                                                 'QThread::currentThread()->property("cachePublication").toJsonObject();\n'
                                                                 '    cacheContext["preparation"] = '
                                                                 'cachePreparation;\n'
                                                                 '    cacheContext["transaction"] = '
                                                                 'QString::number(transaction_id);\n'
                                                                 '    '
                                                                 'QThread::currentThread()->setProperty("cachePublication", '
                                                                 'cacheContext);\n'
                                                                 '    int sequence = 0;',
                                                        'before': '    int sequence = 0;'}],
 'control/reuse.cpp': [{'after': '#include <QJsonDocument>\n'
                                 '#include <QJsonObject>\n'
                                 '#include <QThread>\n'
                                 '#include <QUuid>\n'
                                 '#include <QDebug>\n'
                                 '#include <time.h>\n'
                                 '\n'
                                 'static void cachePublicationEvent(QJsonObject context, const char* event) '
                                 '{\n'
                                 '  struct timespec now{};\n'
                                 '  clock_gettime(CLOCK_MONOTONIC, &now);\n'
                                 '  context["event"] = QString::fromLatin1(event);\n'
                                 '  context["ns"] = QString::number(qint64(now.tv_sec) * 1000000000 + '
                                 'now.tv_nsec);\n'
                                 '  qInfo().noquote() << "CACHE_PUBLICATION" << '
                                 'QJsonDocument(context).toJson(QJsonDocument::Compact);\n'
                                 '}\n'
                                 '\n',
                        'before': ''},
                       {'after': '      if (adequate && !pixel_delivered) {\n'
                                 '        '
                                 'cachePublicationEvent(QThread::currentThread()->property("cachePublicationDelivery").toJsonObject(), '
                                 '"adequate");',
                        'before': '      if (adequate && !pixel_delivered) {'}],
 'early/holonight-file-browser/src/preview/preview_service.cpp': [{'after': '#include "session_pool.h"\n'
                                                                            '#include <QJsonDocument>\n'
                                                                            '#include <QJsonObject>\n'
                                                                            '#include <QThread>\n'
                                                                            '#include <QUuid>\n'
                                                                            '#include <QDebug>\n'
                                                                            '#include <time.h>\n'
                                                                            '\n'
                                                                            'static void '
                                                                            'cachePublicationEvent(QJsonObject '
                                                                            'context, const char* event) {\n'
                                                                            '  struct timespec now{};\n'
                                                                            '  '
                                                                            'clock_gettime(CLOCK_MONOTONIC, '
                                                                            '&now);\n'
                                                                            '  context["event"] = '
                                                                            'QString::fromLatin1(event);\n'
                                                                            '  context["ns"] = '
                                                                            'QString::number(qint64(now.tv_sec) '
                                                                            '* 1000000000 + now.tv_nsec);\n'
                                                                            '  qInfo().noquote() << '
                                                                            '"CACHE_PUBLICATION" << '
                                                                            'QJsonDocument(context).toJson(QJsonDocument::Compact);\n'
                                                                            '}\n'
                                                                            '\n',
                                                                   'before': '#include "session_pool.h"'},
                                                                  {'after': 'struct PreviewResult {\n'
                                                                            '  QJsonObject cacheContext;',
                                                                   'before': 'struct PreviewResult {'},
                                                                  {'after': '  setProperty("cacheService", '
                                                                            'QUuid::createUuid().toString());\n'
                                                                            '  '
                                                                            'worker_->moveToThread(&thread_);',
                                                                   'before': '  '
                                                                             'worker_->moveToThread(&thread_);'},
                                                                  {'after': '  active_job_ = true;\n'
                                                                            '  const auto cacheContext = '
                                                                            'QJsonObject{{"invocation", '
                                                                            'qEnvironmentVariable("HOLONIGHT_CACHE_INVOCATION")},\n'
                                                                            '      {"service", '
                                                                            'property("cacheService").toString()}, '
                                                                            '{"request", '
                                                                            'QUuid::createUuid().toString()}};\n'
                                                                            '  const auto generation = '
                                                                            'generation_;',
                                                                   'before': '  active_job_ = true;\n'
                                                                             '  const auto generation = '
                                                                             'generation_;'},
                                                                  {'after': '[this, path, nativePath, '
                                                                            'generation, cancel, size, '
                                                                            'beforeDispatch, beforeFull, '
                                                                            'stage, options, '
                                                                            'memoryCheckpoint, cacheContext]',
                                                                   'before': '[this, path, nativePath, '
                                                                             'generation, cancel, size, '
                                                                             'beforeDispatch, beforeFull, '
                                                                             'stage, options, '
                                                                             'memoryCheckpoint]'},
                                                                  {'after': 'options, false, '
                                                                            'memoryCheckpoint, defer, '
                                                                            'cacheContext);',
                                                                   'before': 'options, false, '
                                                                             'memoryCheckpoint, defer);'},
                                                                  {'after': 'const '
                                                                            'std::function<bool(QFile&, '
                                                                            'const QString&, const '
                                                                            'PreviewResult&)>& defer = {},\n'
                                                                            '                            '
                                                                            'QJsonObject cacheContext = {}) '
                                                                            '{\n'
                                                                            '  PreviewResult result;\n'
                                                                            '  result.cacheContext = '
                                                                            'cacheContext;',
                                                                   'before': 'const '
                                                                             'std::function<bool(QFile&, '
                                                                             'const QString&, const '
                                                                             'PreviewResult&)>& defer = {}) '
                                                                             '{\n'
                                                                             '  PreviewResult result;'},
                                                                  {'after': '  result.cacheContext["source"] '
                                                                            '= identity;\n'
                                                                            '  result.cacheContext["width"] '
                                                                            '= requestedSize.width();\n'
                                                                            '  result.cacheContext["height"] '
                                                                            '= requestedSize.height();\n'
                                                                            '  '
                                                                            'result.cacheContext["generation"] '
                                                                            '= '
                                                                            'QString::number(result.generation);\n'
                                                                            '  result.cacheContext["worker"] '
                                                                            '= '
                                                                            'QUuid::createUuid().toString();\n'
                                                                            '  '
                                                                            'QThread::currentThread()->setProperty("cachePublication", '
                                                                            'result.cacheContext);\n'
                                                                            '  const auto reply = [&]()',
                                                                   'before': '  const auto reply = [&]()'},
                                                                  {'after': '  result.cacheContext = '
                                                                            'QThread::currentThread()->property("cachePublication").toJsonObject();\n'
                                                                            '  '
                                                                            'result.cacheContext["original_decode"] '
                                                                            '= decodedSource;\n'
                                                                            '  result.cacheContext["tier"] = '
                                                                            'tier ? static_cast<int>(*tier) '
                                                                            ': 0;\n'
                                                                            '  '
                                                                            'result.cacheContext["outcome"] '
                                                                            '= reply.result ? '
                                                                            'static_cast<int>(reply.result->outcome) '
                                                                            ': -1;\n'
                                                                            '  result.runtime = '
                                                                            'reply.runtime;',
                                                                   'before': '  result.runtime = '
                                                                             'reply.runtime;'},
                                                                  {'after': '  bool cachePublished = false;\n'
                                                                            '  if (decodedSource && tier && '
                                                                            'result.raster_outcome',
                                                                   'before': '  if (decodedSource && tier && '
                                                                             'result.raster_outcome'},
                                                                  {'after': '    '
                                                                            'cachePublicationEvent(result.cacheContext, '
                                                                            '"eligible");\n'
                                                                            '    auto progressive = result;\n'
                                                                            '    progressive.final = false;\n'
                                                                            '    if (cancel->load()) {\n'
                                                                            '      return result;\n'
                                                                            '    }\n'
                                                                            '    '
                                                                            'cachePublicationEvent(progressive.cacheContext, '
                                                                            '"enqueue");\n'
                                                                            '    publish(progressive);\n'
                                                                            '    cachePublished = true;\n'
                                                                            '    '
                                                                            'cachePublicationEvent(result.cacheContext, '
                                                                            '"store_entry");\n'
                                                                            '    '
                                                                            'ThumbnailService::storeRaster(file, '
                                                                            'path, identity, *tier, needed, '
                                                                            'result.image, *cancel, stage, '
                                                                            'nativePath);\n'
                                                                            '    '
                                                                            'cachePublicationEvent(result.cacheContext, '
                                                                            '"store_return");',
                                                                   'before': '    '
                                                                             'ThumbnailService::storeRaster(file, '
                                                                             'path, identity, *tier, needed, '
                                                                             'result.image, *cancel, stage, '
                                                                             'nativePath);'},
                                                                  {'after': '  if (!cachePublished) {\n'
                                                                            '    '
                                                                            'cachePublicationEvent(result.cacheContext, '
                                                                            '"enqueue");\n'
                                                                            '    publish(result);\n'
                                                                            '  }\n'
                                                                            '  result.final = true;\n'
                                                                            '  result.image = {};  // EXIF',
                                                                   'before': '  publish(result);\n'
                                                                             '  result.final = true;\n'
                                                                             '  result.image = {};  // EXIF'},
                                                                  {'after': '    display_image_ = '
                                                                            'result.image;\n'
                                                                            '    '
                                                                            'cachePublicationEvent(result.cacheContext, '
                                                                            '"accepted");',
                                                                   'before': '    display_image_ = '
                                                                             'result.image;'},
                                                                  {'after': '  '
                                                                            'QThread::currentThread()->setProperty("cachePublicationDelivery", '
                                                                            'result.cacheContext);\n'
                                                                            '  if (result.final) {\n'
                                                                            '    '
                                                                            'cachePublicationEvent(result.cacheContext, '
                                                                            '"final");\n'
                                                                            '  }\n'
                                                                            '  notifyChanged();\n'
                                                                            '  if (result.final && '
                                                                            'mime_type_',
                                                                   'before': '  notifyChanged();\n'
                                                                             '  if (result.final && '
                                                                             'mime_type_'}],
 'early/holonight-images/src/isolated/runtime.cpp': [{'after': '#include "runtime.h"\n#include <QJsonObject>',
                                                      'before': '#include "runtime.h"'},
                                                     {'after': '  const QString cachePreparation = '
                                                               'QUuid::createUuid().toString();\n'
                                                               '  int transaction_id = 1;',
                                                      'before': '  int transaction_id = 1;'},
                                                     {'after': '    auto cacheContext = '
                                                               'QThread::currentThread()->property("cachePublication").toJsonObject();\n'
                                                               '    cacheContext["preparation"] = '
                                                               'cachePreparation;\n'
                                                               '    cacheContext["transaction"] = '
                                                               'QString::number(transaction_id);\n'
                                                               '    '
                                                               'QThread::currentThread()->setProperty("cachePublication", '
                                                               'cacheContext);\n'
                                                               '    int sequence = 0;',
                                                      'before': '    int sequence = 0;'}],
 'early/reuse.cpp': [{'after': '#include <QJsonDocument>\n'
                               '#include <QJsonObject>\n'
                               '#include <QThread>\n'
                               '#include <QUuid>\n'
                               '#include <QDebug>\n'
                               '#include <time.h>\n'
                               '\n'
                               'static void cachePublicationEvent(QJsonObject context, const char* event) {\n'
                               '  struct timespec now{};\n'
                               '  clock_gettime(CLOCK_MONOTONIC, &now);\n'
                               '  context["event"] = QString::fromLatin1(event);\n'
                               '  context["ns"] = QString::number(qint64(now.tv_sec) * 1000000000 + '
                               'now.tv_nsec);\n'
                               '  qInfo().noquote() << "CACHE_PUBLICATION" << '
                               'QJsonDocument(context).toJson(QJsonDocument::Compact);\n'
                               '}\n'
                               '\n',
                      'before': ''},
                     {'after': '      if (adequate && !pixel_delivered) {\n'
                               '        '
                               'cachePublicationEvent(QThread::currentThread()->property("cachePublicationDelivery").toJsonObject(), '
                               '"adequate");',
                      'before': '      if (adequate && !pixel_delivered) {'}]}


def protocol():
    arms = ['control', 'early']
    entries = [(arm, None) for arm in arms]
    for pair in range(5):
        entries += [(arm, pair) for arm in (arms if pair % 2 == 0 else list(reversed(arms)))]
    schedule = [dict(index=i, arm=arm, pair=pair, warmup=pair is None, count=1)
                for i, (arm, pair) in enumerate(entries)]
    return dict(version=1, scenario='startup', requested_size=[256, 256], schedule=schedule,
        processes=12, measured=10, warmups=2, retries=0, offscreen=True,
        private_cache=True, private_source=True, workload_seconds=30, shared_cleanup_seconds=5,
        cache_flushing=False, affinity_changes=False, artificial_load=False,
        clock='CLOCK_MONOTONIC nanoseconds',
        identities=['invocation', 'service', 'request', 'worker', 'preparation', 'transaction'],
        events=['eligible', 'store_entry', 'store_return', 'enqueue', 'accepted', 'adequate', 'final'],
        supporting_order='store_entry < adequate < store_return',
        native_prerequisites=['target change during commit', 'cancellation', 'timeout', 'shutdown',
            'store failure', 'pixel/metadata ordering', 'cache availability at final', 'session cleanup'],
        future_bindings=['native binaries', 'installed providers', 'runtime payloads', 'protected-generation leases',
            'actual loading identities or explicit unavailable evidence'],
        execution_capability='unvalidated', native_correctness='unvalidated', execution_commands=[],
        qualification='78/80 unchanged', streaming='Deferred', validation_reuse='Deferred',
        candidate_selection='Evidence insufficient', performance_claims=False)


def reconstruct(data, arm, name):
    edits = EDITS.get(arm + '/' + name, [])
    text = data.decode() if edits else None
    for edit in reversed(edits):
        h.require(text.count(edit['after']) == 1, 'private edit multiplicity: ' + name)
        text = text.replace(edit['after'], edit['before'], 1)
    return text.encode() if edits else data


def verify(root):
    h.sealed(root)
    assessment = h.read(root / 'assessment.json')
    h.require(assessment['executed_commands'] == [] and
        assessment['native_correctness'] == assessment['execution_capability'] == 'unvalidated' and
        assessment['decision'] == 'Evidence insufficient', 'zero-execution assessment')
    h.require(assessment['status'] in ('prepared', 'blocked'), 'invalid preparation status')
    tools = h.read(root / 'tools.json')
    h.require(tools == e.snapshots(), 'tool identity drift')
    expected = {'tools.json', 'assessment.json', 'REPORT.md', 'integrity.json'}
    h.require(len({Path(p).name for p in tools}) == len(tools), 'tool basename collision')
    for name, digest in tools.items():
        target = 'tools/' + Path(name).name
        h.require(h.digest(root / target) == digest, 'tool snapshot drift')
        expected.add(target)
    if assessment['status'] == 'blocked':
        h.require(bool(assessment.get('failure')), 'blocked without reason')
        # Partial artifacts are retained, never interpreted as accepted variants.
        # They may only be members of the preparation namespace, never execution output.
        for name in h.inventory(root):
            h.require(name in expected | {'seal.json', 'inputs.json', 'protocol.json', '3200x2400.png',
                'anchors.json', 'control-inventory.json', 'early-inventory.json'} or
                name.startswith(('control/source/', 'early/source/', 'control/harness-source/',
                                 'early/harness-source/')) or
                name in {a + '-' + n + '.diff' for a in e.ARMS for n in ('preview_service.cpp', 'runtime.cpp', 'reuse.cpp')},
                'unexpected blocked package member')
        return dict(status='passed', outcome='blocked', decision='Evidence insufficient',
                    evidence_seal=h.digest(root / 'seal.json'))
    h.require(h.read(root / 'integrity.json') == dict(inputs_unchanged=True, tools_unchanged=True), 'preparation recheck failed')
    inputs = h.read(root / 'inputs.json')
    h.require(inputs == e.retained(), 'consumed provenance binding')
    h.require(h.read(root / 'protocol.json') == protocol(), 'protocol drift')
    expected |= {'inputs.json', 'protocol.json', '3200x2400.png', 'anchors.json'}
    h.require(h.digest(root / '3200x2400.png') == inputs['fixture']['sha256'], 'fixture drift')
    anchors = {}
    for arm in e.ARMS:
        for group, origin, inventory in [('source', e.Q / 'C/source', inputs['source']),
                                         ('harness-source', e.Q / 'harness-source', inputs['harness'])]:
            for name in inventory:
                key = arm + '/' + group + '/' + name
                expected.add(key)
                data = (root / key).read_bytes()
                h.require(reconstruct(data, arm, name) == (origin / name).read_bytes(), 'unallowed source edit: ' + key)
                edits = EDITS.get(arm + '/' + name)
                if edits:
                    anchors[key] = edits
                    patch = arm + '-' + Path(name).name + '.diff'
                    expected.add(patch)
                    original = (origin / name).read_text()
                    diff = ''.join(difflib.unified_diff(original.splitlines(True), data.decode().splitlines(True),
                                  fromfile='frozen/' + name, tofile=key))
                    h.require((root / patch).read_text() == diff, 'private diff drift')
        inventory_file = arm + '-inventory.json'
        expected.add(inventory_file)
        h.require(h.read(root / inventory_file) == h.inventory(root / arm), 'complete variant inventory')
    h.require(h.read(root / 'anchors.json') == anchors, 'transformation anchor drift')
    h.require(set(h.inventory(root)) == expected | {'seal.json'}, 'complete package membership')
    h.require(h.recheck(inputs['inventories'], inputs['files']), 'inputs changed during verification')
    return dict(status='passed', outcome='prepared', native_correctness='unvalidated',
        execution_capability='unvalidated', decision='Evidence insufficient',
        evidence_seal=h.digest(root / 'seal.json'), imports_preparer=False)


def observation(events):
    """Validate one future event fixture. Values are monotonic integer nanoseconds."""
    names = protocol()['events']
    h.require(len(events) == len(names) and {r['event'] for r in events} == set(names), 'event membership')
    by_name = {r['event']: r for r in events}
    identity = protocol()['identities'] + ['source', 'width', 'height', 'generation', 'original_decode', 'tier', 'outcome']
    first = by_name['eligible']
    for key in protocol()['identities'] + ['source', 'generation']:
        h.require(isinstance(first.get(key), str) and bool(first[key]), 'missing explicit identity')
    h.require(first['width'] == first['height'] == 256 and first['original_decode'] is True and
              type(first['tier']) is int and first['tier'] > 0 and first['outcome'] == 0, 'ineligible decode')
    for row in events:
        h.require(all(row.get(k) == first.get(k) for k in identity), 'cross-identity join')
        h.require(type(row['ns']) is int and row['ns'] >= 0 and
                  not row.get('cancelled', False) and not row.get('stale', False), 'invalid delivery/time')
    times = {k: v['ns'] for k, v in by_name.items()}
    h.require(times['eligible'] <= times['store_entry'] < times['store_return'] <= times['final'] and
              times['eligible'] <= times['enqueue'] <= times['accepted'] <= times['adequate'] <= times['final'],
              'malformed event ordering')
    return times['store_entry'] < times['adequate'] < times['store_return']


def outcome(rows):
    try:
        h.require([r['schedule'] for r in rows] == protocol()['schedule'], 'incomplete schedule')
        supports = []
        invocations = set()
        for row in rows:
            h.require(row['correct_pixels'] is True and row['correct_metadata'] is True and
                      row['cache_available_at_final'] is True and row['cleanup_passed'] is True and
                      row['native_bindings_passed'] is True, 'correctness or native bindings failure')
            supporting = observation(row['events'])
            invocation = row['events'][0]['invocation']
            h.require(invocation not in invocations, 'reused process invocation')
            invocations.add(invocation)
            if row['schedule']['arm'] == 'control':
                times = {v['event']: v['ns'] for v in row['events']}
                h.require(times['store_return'] <= times['enqueue'], 'control publication before store')
            if not row['schedule']['warmup'] and row['schedule']['arm'] == 'early':
                supports.append(supporting)
        return 'overlap observed' if any(supports) else 'overlap not observed in this population'
    except (ValueError, KeyError, TypeError):
        return 'Evidence insufficient'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, output = args.evidence.absolute(), args.output.absolute()
    h.require(output == output.resolve() and not output.exists() and
              not output.is_relative_to(root) and not root.is_relative_to(output), 'verification collision/overlap')
    try:
        result = verify(root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = dict(status='failed', failure=str(error), decision='Evidence insufficient')
    h.write(output, result)
    print(h.json.dumps(result, indent=2))
    sys.exit(result['status'] != 'passed')
