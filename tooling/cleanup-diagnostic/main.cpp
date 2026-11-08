// SPDX-License-Identifier: GPL-3.0-or-later
#include <QBuffer>
#include <QCoreApplication>
#include <QCryptographicHash>
#include <QElapsedTimer>
#include <QFile>
#include <QFileInfo>
#include <QJsonDocument>
#include <QJsonObject>
#include <chrono>
#include <condition_variable>
#include <holonight_images/isolated.h>
#include <mutex>
#include <thread>
using namespace HolonightImages;
namespace {
constexpr Limits limits{.inputBytes = 256 * 1024 * 1024,
                        .sourcePixels = 64000000,
                        .sourceExtent = 32768,
                        .decodedBytes = 256 * 1024 * 1024,
                        .metadataBytes = 1024 * 1024,
                        .tiffMetadataBytes = 64 * 1024 * 1024,
                        .metadataRecords = 4096};
// Same three-second cooperative deadline as the preview service, including
// capture.
struct Deadline {
  std::atomic_bool cancelled{false};
  std::mutex mutex;
  std::condition_variable condition;
  bool done = false;
  std::thread thread{[this] {
    std::unique_lock lock(mutex);
    if (!condition.wait_for(lock, std::chrono::seconds(3),
                            [this] { return done; }))
      cancelled = true;
  }};
  ~Deadline() {
    {
      std::lock_guard lock(mutex);
      done = true;
    }
    condition.notify_one();
    thread.join();
  }
};
} // namespace
int main(int argc, char **argv) {
  QCoreApplication application(argc, argv);
  const auto args = application.arguments();
  if (args.size() != 7)
    return 2; // runtime, new JSONL output, four frozen fixtures
  if (!QFileInfo(args[1]).isAbsolute() ||
      !QFileInfo::exists(args[1] + "/manifest.json"))
    return 2;
  QFile output(args[2]);
  if (!output.open(QIODevice::WriteOnly | QIODevice::NewOnly))
    return 2;
  IsolatedClient client(args[1]);
  QElapsedTimer clock;
  clock.start();
  int operations = 0;
  int cycles = 0;
  auto record = [&](const auto &result, const QString &operation,
                    const QString &fixture, const QByteArray &hash) {
    QJsonObject row{{"kind", "diagnostic-only"},
                    {"id", ++operations},
                    {"cycle", cycles},
                    {"operation", operation},
                    {"fixture", fixture},
                    {"sha256", QString::fromLatin1(hash)},
                    {"runtime", static_cast<int>(result.runtime)},
                    {"elapsed_ms", result.elapsedMilliseconds},
                    {"outcome", result.result
                                    ? static_cast<int>(result.result->outcome)
                                    : -1},
                    {"diagnostic", result.diagnostic}};
    output.write(QJsonDocument(row).toJson(QJsonDocument::Compact) + '\n');
    output.flush();
    return result.runtime == RuntimeStatus::CleanupFailure;
  };
  for (; cycles < 1000 && clock.elapsed() < 600000; ++cycles) {
    const auto fixture = args[3 + cycles % 4];
    QFile source(fixture);
    if (!source.open(QIODevice::ReadOnly))
      return 2;
    QCryptographicHash hash(QCryptographicHash::Sha256);
    if (!hash.addData(&source))
      return 2;
    const auto digest = hash.result().toHex();
    {
      Deadline deadline;
      const auto result = client.inspect(source, limits, deadline.cancelled);
      if (record(result, "inspect", fixture, digest))
        return 1;
    }
    if (clock.elapsed() >= 600000)
      break;
    QByteArray png;
    {
      Deadline deadline;
      const auto result =
          client.decode(source, {.limits = limits, .bound = {1024, 1024}},
                        deadline.cancelled);
      if (record(result, "source-decode", fixture, digest))
        return 1;
      if (result.result && result.result->outcome == Outcome::Success) {
        QBuffer encoded(&png);
        if (!encoded.open(QIODevice::WriteOnly) ||
            !result.result->image.save(&encoded, "PNG"))
          return 2;
      }
    }
    if (clock.elapsed() >= 600000)
      break;
    if (!png.isEmpty()) {
      QBuffer cached(&png);
      cached.open(QIODevice::ReadOnly);
      Deadline deadline;
      const auto result =
          client.decode(cached,
                        {.limits = limits,
                         .bound = {1024, 1024},
                         .orientation = OrientationPolicy::Ignore},
                        deadline.cancelled);
      if (record(result, "cached-png-decode", fixture,
                 QCryptographicHash::hash(png, QCryptographicHash::Sha256)
                     .toHex()))
        return 1;
    }
  }
  output.write(QJsonDocument(QJsonObject{{"kind", "summary"},
                                         {"cycles", cycles},
                                         {"operations", operations},
                                         {"elapsed_ms", clock.elapsed()}})
                   .toJson(QJsonDocument::Compact) +
               '\n');
  return 0;
}
