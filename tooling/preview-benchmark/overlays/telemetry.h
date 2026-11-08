// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
// Only copied into diagnostic archives. Never included by production sources.
#include <QDirIterator>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QSet>

#include <atomic>
#include <chrono>
#include <cstdio>
#include <mutex>
#include <unistd.h>
#include <vector>
namespace PreviewEvidence {
inline qint64 now() {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::steady_clock::now().time_since_epoch())
      .count();
}
inline thread_local QString consumer;
inline thread_local QString operation;
inline std::atomic<quint64> sequence{0};
inline std::atomic_bool cleanupFailed{false};
struct Buffer {
  std::mutex mutex;
  std::vector<QJsonObject> records;
  quint64 dropped = 0;
  void flush() {
    const std::lock_guard lock(mutex);
    for (const auto& row : records) {
      const auto bytes = QJsonDocument(row).toJson(QJsonDocument::Compact);
      std::fputs("HN_DIAG ", stderr);
      std::fwrite(bytes.data(), 1, bytes.size(), stderr);
      std::fputc('\n', stderr);
    }
    const auto trailer = QJsonDocument(QJsonObject{{"event", "flush"},
                                                   {"pid", int(getpid())},
                                                   {"records", int(records.size())},
                                                   {"dropped", double(dropped)}})
                             .toJson(QJsonDocument::Compact);
    std::fprintf(stderr, "HN_DIAG %s\n", trailer.constData());
    std::fflush(stderr);
    records.clear();
    dropped = 0;
  }
  ~Buffer() { flush(); }
};
inline Buffer buffer;
inline void event(const QString& name, QJsonObject fields = {}) {
  fields.insert("event", name);
  fields.insert("pid", int(getpid()));
  fields.insert("consumer", consumer);
  fields.insert("operation", operation);
  fields.insert("ns", QString::number(now()));
  const std::lock_guard lock(buffer.mutex);
  if (buffer.records.size() < 16384)
    buffer.records.push_back(std::move(fields));
  else
    ++buffer.dropped;
}
struct Context {
  QString& slot;
  QString previous;
  Context(QString& value, QString next) : slot(value), previous(value) { slot = std::move(next); }
  ~Context() { slot = previous; }
};
struct Phase {
  QString name;
  qint64 start = now();
  bool ended = false;
  explicit Phase(QString value) : name(std::move(value)) {}
  void end() {
    if (!ended) {
      const auto finish = now();
      event(name, {{"begin_ns", QString::number(start)}, {"end_ns", QString::number(finish)}});
      ended = true;
    }
  }
  ~Phase() { end(); }
};
inline void settledScopes() {
  QSet<QString> groups;
  {
    const std::lock_guard lock(buffer.mutex);
    for (const auto& record : buffer.records) {
      if (record["event"] == "scope") groups.insert(record["group"].toString());
    }
  }
  QJsonArray observations;
  int scopes = 0;
  int processes = 0;
  bool available = true;
  for (const auto& group : groups) {
    const bool exists = QFileInfo::exists(group);
    scopes += exists;
    QJsonObject observation{{"group", group}, {"exists", exists}};
    if (exists) {
      QFile events(group + "/cgroup.events");
      const bool readable = events.open(QIODevice::ReadOnly);
      available = available && readable;
      observation["events"] = readable ? QString::fromUtf8(events.readAll()) : QString{};
      QStringList paths{group + "/cgroup.procs"};
      QDirIterator entries(group, QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);
      while (entries.hasNext()) paths.append(entries.next() + "/cgroup.procs");
      for (const auto& path : paths) {
        QFile file(path);
        if (!file.open(QIODevice::ReadOnly)) {
          available = false;
          continue;
        }
        for (const auto& line : file.readAll().split('\n'))
          if (!line.trimmed().isEmpty()) ++processes;
      }
    }
    observations.append(observation);
  }
  event("post_drain_scopes", {{"scopes", scopes},
                              {"processes", available ? QJsonValue(processes) : QJsonValue()},
                              {"observations", observations},
                              {"tracked_scopes", int(groups.size())}});
}
inline QString requestId(const void* pointer) { return QString::number(reinterpret_cast<quintptr>(pointer), 16); }
}  // namespace PreviewEvidence
