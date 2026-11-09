// SPDX-License-Identifier: GPL-3.0-or-later
#include "decoder_gate.h"

#include <QCoreApplication>
#include <QDir>
#include <QElapsedTimer>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QQuickTextureFactory>
#include <QTemporaryDir>

#include <HolonightFileBrowser/preview_quick/thumbnail_provider.h>
#include <array>
#include <memory>
#include <mutex>

namespace {
constexpr int batchSize = 16;
struct Observation {
  bool started = false;
  bool cancelled = false;
  bool finished = false;
  bool delivered = false;
  QString error;
  QString diagnostic;
  int runtime = -1;
};
struct Batch {
  std::mutex mutex;
  std::array<Observation, batchSize> observations;
  DecoderGate gate;
};
bool pump(const std::function<bool()>& done) {
  QElapsedTimer clock;
  clock.start();
  while (!done() && clock.elapsed() < 30000) {
    QCoreApplication::processEvents();
    QThread::usleep(100);
  }
  return done();
}
}  // namespace
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  const auto args = app.arguments();
  const QStringList fixtureNames{"160x80.png", "1600x1200.png", "3200x2400.png", "oriented.jpg"};
  if (args.size() == 2 && args[1] == "--describe-workload") {
    QJsonArray copies;
    for (int i = 0; i < batchSize; ++i) copies.append(fixtureNames[i % 4]);
    QFile output;
    if (!output.open(stdout, QIODevice::WriteOnly)) return 2;
    output.write(QJsonDocument(QJsonObject{{"fixtures", copies}, {"scheduler_threads", 2}, {"box_pixels", 256}})
                     .toJson(QJsonDocument::Compact));
    return 0;
  }
  if (args.size() != 6 || !QStringList{"cold", "warm", "cancel"}.contains(args[3])) return 2;
  bool ok = false;
  const int attempts = args[4].toInt(&ok);
  if (!ok || attempts < 1 || attempts > 100) return 2;
  QFile output(args[5]);
  if (!output.open(QIODevice::WriteOnly | QIODevice::NewOnly)) return 2;
  QTemporaryDir directory;
  if (!directory.isValid()) return 2;
  qputenv("XDG_CACHE_HOME", directory.filePath("cache").toUtf8());
  const QDir fixtures(args[2]);
  for (int attempt = 0; attempt < attempts; ++attempt) {
    QStringList paths;
    for (int i = 0; i < batchSize; ++i) {
      const auto fixture = fixtures.filePath(fixtureNames[i % 4]);
      const auto path =
          directory.filePath(QString::number(attempt) + "-" + QString::number(i) + "." + fixture.section('.', -1));
      if (!QFile::copy(fixture, path)) return 2;
      paths.append(path);
    }
    Batch state;
    ThumbnailProvider provider(
        [&](const ThumbnailRequest& request, const std::atomic_bool& cancelled) {
          const int i = int(paths.indexOf(request.path));
          {
            const std::lock_guard lock(state.mutex);
            if (!state.gate.admit()) {
              return ThumbnailResult{.error = QStringLiteral("Stopped after cleanup failure")};
            }
            state.observations.at(i).started = true;
          }
#ifdef ISOLATED
          const auto result = decodeThumbnail(request, cancelled, {args[1]});
#else
          const auto result = decodeThumbnail(request, cancelled);
#endif
          {
            const std::lock_guard lock(state.mutex);
            state.observations.at(i).error = result.error;
#ifdef ISOLATED
            state.observations.at(i).runtime = int(result.runtime);
            state.observations.at(i).diagnostic = result.diagnostic;
            state.gate.complete(result.runtime == HolonightImages::RuntimeStatus::CleanupFailure);
#endif
          }
          return result;
        },
        2);
    auto run = [&](bool cancel) {
      std::array<std::unique_ptr<QQuickImageResponse>, batchSize> responses;
      QElapsedTimer clock;
      clock.start();
      for (int i = 0; i < batchSize; ++i) {
        responses[i].reset(provider.requestImageResponse(ThumbnailProvider::idFor(paths[i], 256, 0), {}));
        QObject::connect(responses[i].get(), &QQuickImageResponse::finished, &app, [&, i] {
          std::unique_ptr<QQuickTextureFactory> texture(responses[i]->textureFactory());
          const auto image = texture ? texture->image() : QImage{};
          const std::lock_guard lock(state.mutex);
          auto& observation = state.observations[i];
          observation.finished = true;
          observation.delivered = !observation.cancelled && !image.isNull() && image.width() > 0 &&
                                  image.height() > 0 && image.width() <= 256 && image.height() <= 256;
        });
      }
      if (cancel) {
        for (int i = 0; i < 12; ++i) {
          {
            const std::lock_guard lock(state.mutex);
            state.observations[i].cancelled = true;
          }
          responses[i]->cancel();
        }
      }
      const bool drained = pump([&] {
        const std::lock_guard lock(state.mutex);
        return provider.pendingCount() == 0 && std::all_of(state.observations.begin(), state.observations.end(),
                                                           [](const auto& row) { return row.finished; });
      });
      const double elapsed = clock.nsecsElapsed() / 1000000.0;
      int started = 0, before = 0, after = 0, delivered = 0, finished = 0;
      QJsonArray operations;
      {
        const std::lock_guard lock(state.mutex);
        int sourceIndex = 0;
        for (const auto& row : state.observations) {
          started += row.started;
          before += row.cancelled && !row.started;
          after += row.cancelled && row.started;
          delivered += row.delivered;
          finished += row.finished;
          operations.append(QJsonObject{{"source_fixture", fixtureNames[sourceIndex++ % 4]},
                                        {"started", row.started},
                                        {"cancelled", row.cancelled},
                                        {"finished", row.finished},
                                        {"validated_image", row.delivered},
                                        {"error", row.error},
                                        {"runtime", row.runtime},
                                        {"diagnostic", row.diagnostic}});
        }
      }
      return QJsonObject{{"issued", batchSize},
                         {"started", started},
                         {"cancelled_before_start", before},
                         {"cancelled_after_start", after},
                         {"delivered", delivered},
                         {"finished", finished},
                         {"drained", drained},
                         {"pending", provider.pendingCount()},
                         {"wall_ms", elapsed},
                         {"cleanup_failure", state.gate.failed()},
                         {"operations", operations},
                         {"success", drained && delivered == (cancel ? 4 : 16) && !state.gate.failed()}};
    };
    QJsonObject setup;
    if (args[3] == "warm") {
      setup = run(false);
      if (setup["success"].toBool()) {
        const std::lock_guard lock(state.mutex);
        state.observations = {};
      }
    }
    QJsonObject row{{"attempt", attempt},
                    {"workload", args[3]},
                    {"fixture_directory", args[2]},
                    {"fixture_cycle", QJsonArray::fromStringList(fixtureNames)},
                    {"scheduler_threads", 2},
                    {"box_pixels", 256},
                    {"setup", setup}};
    if (setup.isEmpty() || setup["success"].toBool())
      row["sample"] = run(args[3] == "cancel");
    else
      row["incomplete"] = true;
    const auto bytes = QJsonDocument(row).toJson(QJsonDocument::Compact) + '\n';
    if (output.write(bytes) != bytes.size() || !output.flush()) return 3;
    if (state.gate.failed()) return 20;
    if (row["incomplete"].toBool() || !row["sample"].toObject()["success"].toBool()) return 1;
  }
  return 0;
}
