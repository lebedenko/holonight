#pragma once
#include "trace.h"
#include <QJsonDocument>
#include <QJsonObject>
#include <QString>
#include <chrono>
#include <condition_variable>
#include <fstream>
#include <string>
#include <vector>
namespace CancellationDiagnostic {
// Metadata completion deliberately has no image payload. Observe status only.
template <class Result> bool successfulResult(const Result& result) {
  using Runtime = decltype(result.runtime);
  using Outcome = typename decltype(result.raster_outcome)::value_type;
  using Error = decltype(result.error.kind);
  return result.runtime == Runtime::Success && result.raster_outcome == Outcome::Success &&
         result.error.kind == Error::None;
}

inline std::mutex mutex;
inline std::condition_variable changed;
inline std::ofstream ledger, barriers;
inline std::string scenario;
inline unsigned long long order = 0, primary = 0;
inline bool failed = false, released_all = false;
inline std::map<std::string, bool> reached, released;
inline std::vector<QJsonObject> records;
inline void recordLocked(const char* event, quint64 selection, QJsonObject fields, bool barrier) {
  const auto c = StandbyTrace::current;
  timespec t{}; clock_gettime(CLOCK_MONOTONIC, &t);
  fields.insert("event", event); fields.insert("order", qint64(++order));
  fields.insert("ns", qint64(t.tv_sec)*1000000000LL+t.tv_nsec);
  fields.insert("pid", int(getpid())); fields.insert("tid", qint64(syscall(SYS_gettid)));
  fields.insert("version", 3); fields.insert("service", qint64(c.service));
  fields.insert("observation", qint64(c.observation)); fields.insert("job", qint64(c.job));
  fields.insert("worker", qint64(c.worker)); fields.insert("preparation", qint64(c.preparation));
  fields.insert("role", c.role); fields.insert("selection", qint64(selection));
  records.push_back(fields);
  auto& stream = barrier ? barriers : ledger;
  stream << QJsonDocument(fields).toJson(QJsonDocument::Compact).constData() << '\n'; stream.flush();
  changed.notify_all();
}
inline void probe(const char* event, quint64 selection=0, QJsonObject fields={}) {
  std::lock_guard lock(mutex);
  if (std::string(event)=="submit" && !primary) primary=StandbyTrace::current.job;
  recordLocked(event, selection, fields, false);
}
inline bool seen(const std::string& event, unsigned long long job=0) {
  std::lock_guard lock(mutex);
  for (const auto& row: records)
    if (row["event"].toString().toStdString()==event && (!job || row["job"].toInteger()==qint64(job))) return true;
  return false;
}
inline void release(const std::string& name) {
  std::lock_guard lock(mutex); released[name]=true;
  recordLocked((name+"_release").c_str(), 0, {}, true);
}
inline void releaseAll() {
  std::lock_guard lock(mutex); released_all=true; changed.notify_all();
}
// Called only by the diagnostic supervisor; never accesses a QObject.
inline bool superviseDestruction(StandbyTrace::Context context, std::chrono::milliseconds timeout) {
  StandbyTrace::Bind bind(context);
  std::unique_lock lock(mutex);
  const bool acknowledged = context.service && context.observation &&
      changed.wait_for(lock, timeout, [&] {
        for (const auto& row : records)
          if (row["event"] == "destructor_cancel" && row["cancelled"].toBool() &&
              row["service"].toInteger() == qint64(context.service) &&
              row["observation"].toInteger() == qint64(context.observation)) return true;
        return false;
      });
  if (acknowledged) {
    released["active"] = true;
    recordLocked("active_release", 0, {}, true);
  } else {
    failed = true;
    released_all = true;
    changed.notify_all();
  }
  return acknowledged;
}
inline bool gate(const std::string& name) {
  std::unique_lock lock(mutex);
  if (reached[name]) return true;
  reached[name]=true; recordLocked((name+"_reached").c_str(),0,{},true);
  bool ok=changed.wait_for(lock,std::chrono::seconds(1),[&]{return released[name] || released_all;});
  if (!ok) { failed=true; released_all=true; recordLocked("barrier_timeout",0,{{"gate",QString::fromStdString(name)}},true); }
  recordLocked((name+"_resumed").c_str(),0,{},true);
  return ok;
}
inline void preparation(const std::atomic_bool* cancelled) {
  bool hold;
  { std::lock_guard lock(mutex); hold=scenario=="preparation" && !reached["preparation"]; }
  if (hold) { gate("preparation"); probe("preparation_cancel_observed",0,{{"cancelled",cancelled && cancelled->load()}}); }
}
inline void retirement() {
  bool hold;
  { std::lock_guard lock(mutex); hold=scenario=="cleanup" && primary && StandbyTrace::current.job==primary && !reached["retirement"]; }
  if (hold) gate("retirement");
}
}
