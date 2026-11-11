// SPDX-License-Identifier: GPL-3.0-or-later
#ifdef PREVIEW_DIAGNOSTIC_HEADER
#include PREVIEW_DIAGNOSTIC_HEADER
#endif
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTemporaryDir>
#include <QThread>

#include <HolonightFileBrowser/preview/image_policy.h>
#include <HolonightFileBrowser/preview/preview_service.h>
#include <HolonightFileBrowser/preview/thumbnail_decoder.h>
#include <atomic>
#include <cstdio>
#include <holonight_thumbnails/cache.h>
#include <memory>
#include <sys/resource.h>
#include <sys/stat.h>

namespace {
using Consumer = PreviewService::PreviewConsumer;
std::atomic_bool cleanupFailure{false};
void messages(QtMsgType type, const QMessageLogContext& context, const QString& message) {
  if (message.startsWith("Preview runtime failure 4")) {
    cleanupFailure.store(true);
  }
  Q_UNUSED(type)
  Q_UNUSED(context)
  std::fprintf(stderr, "%s\n", qPrintable(message));
}
void target(PreviewService& service, const QString& path) {
  service.setTarget(path, false, 0, {}, S_IFREG | 0600, false, {}, {});
}
bool adequate(const PreviewService& service, QSize required) {
  return service.hasImage() && (required.isEmpty() || (service.image().width() >= required.width() &&
                                                       service.image().height() >= required.height()));
}
bool settle(PreviewService& service, QSize required = {}) {
  QElapsedTimer clock;
  clock.start();
  while ((service.busy() || !adequate(service, required)) && clock.elapsed() < 10000) {
    if (!service.busy() && service.previewErrorKind() != PreviewService::PreviewErrorKind::None) {
      break;
    }
    QCoreApplication::processEvents();
    QThread::usleep(100);
  }
  return !service.busy() && adequate(service, required);
}
double cpu(const rusage& usage) {
  return usage.ru_utime.tv_sec * 1000.0 + usage.ru_utime.tv_usec / 1000.0 + usage.ru_stime.tv_sec * 1000.0 +
         usage.ru_stime.tv_usec / 1000.0;
}
}  // namespace

// One invocation is one alternating block. Fixture preparation and private source
// copies precede timing. No global cache flush, tracing, or resource polling.
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  qInstallMessageHandler(messages);
  if (argc != 6) {
    std::fprintf(stderr, "usage: preview-benchmark RUNTIME FIXTURE SCENARIO COUNT OUTPUT\n");
    return 2;
  }
  const QString runtime = QString::fromLocal8Bit(argv[1]);
  const QString fixture = QString::fromLocal8Bit(argv[2]);
  const QString scenario = QString::fromLocal8Bit(argv[3]);
  bool valid = false;
  const int count = QString::fromLocal8Bit(argv[4]).toInt(&valid);
  if (!valid || count < 1 || count > 1000 ||
      !QStringList{"first", "uncached", "disk", "memory", "upgrade", "burst", "grid-decode"}.contains(scenario)) {
    return 2;
  }
  QTemporaryDir directory;
  if (!directory.isValid()) {
    return 3;
  }
  qputenv("XDG_CACHE_HOME", directory.filePath("cache").toUtf8());
  auto make = [&] {
#ifdef ISOLATED
    auto service = std::make_unique<PreviewService>(HolonightFileBrowser::ImageRuntimeOptions{runtime});
#else
    auto service = std::make_unique<PreviewService>();
#endif
    service->setRequestedSize(Consumer::Pane, {256, 256});
    service->setRequestedSize(Consumer::QuickLook, {1280, 960});
    return service;
  };
  QStringList paths;
  for (int index = 0; index < count + 21; ++index) {
    const auto path = directory.filePath(QString::number(index) + '.' + fixture.section('.', -1));
    if (!QFile::copy(fixture, path)) {
      return 4;
    }
    paths.append(path);
  }
  QFile referenceSource(fixture);
  if (!referenceSource.open(QIODevice::ReadOnly)) {
    return 7;
  }
  const std::atomic_bool cancelled{false};
  const auto inspection = HolonightImages::inspect(referenceSource, kPreviewImageLimits, cancelled);
  const auto& sourceFacts = inspection.metadata.facts;
  const auto referenceBound = scenario == "upgrade" ? QSize(1280, 960) : QSize(256, 256);
  const auto requiredSize = ThumbnailService::requiredSize(inspection.orientedSize, referenceBound);
  const auto tier = ThumbnailService::tierForSize(requiredSize);
  const auto decodeBound = tier ? QSize(static_cast<int>(*tier), static_cast<int>(*tier)) : referenceBound;
  const auto expected =
      HolonightImages::decode(referenceSource, {.limits = kPreviewImageLimits, .bound = decodeBound}, cancelled);
  if (inspection.outcome != HolonightImages::Outcome::Success ||
      expected.outcome != HolonightImages::Outcome::Success) {
    return 8;
  }
  auto service = make();
  QJsonArray samples;
  for (int index = 0; index < count; ++index) {
    const auto& path = paths[index];
    bool setupOk = true;
    if (scenario == "first") {
      service = make();
    } else if (scenario != "grid-decode") {
      service->setQuickLookActive(false);
      service->clear();
      target(*service, scenario == "uncached" || scenario == "burst" ? paths.last() : path);
      setupOk = settle(*service);
      if (scenario != "upgrade") {
        service->clear();
      }
      if (scenario == "disk") {
        const auto cacheTier =
            ThumbnailService::tierForSize(ThumbnailService::requiredSize(inspection.orientedSize, {256, 256}));
        setupOk =
            setupOk && cacheTier &&
            QFileInfo::exists(HolonightThumbnails::cachePath(QUrl::fromLocalFile(path), static_cast<int>(*cacheTier)));
        service = make();
      }
    }
    if (cleanupFailure.load() || !setupOk) {
      samples.append(
          QJsonObject{{"incomplete", true}, {"cleanup_failure", cleanupFailure.load()}, {"setup_success", setupOk}});
      break;
    }
#ifdef PREVIEW_DIAGNOSTIC_HEADER
    if (PreviewEvidence::cleanupFailed.load()) {
      samples.append(QJsonObject{{"incomplete", true}, {"cleanup_failure", true}, {"setup_success", setupOk}});
      break;
    }
#endif
    QElapsedTimer clock;
    double first = -1;
    double final = -1;
    bool observing = false;
    const auto required =
        scenario == "upgrade" ? ThumbnailService::requiredSize(service->sourcePixelSize(), {1280, 960}) : requiredSize;
    auto connection = QObject::connect(service.get(), &PreviewService::changed, &app, [&] {
      if (!observing) {
        return;
      }
      // An upgrade must produce new resolution, not count existing pane pixels.
      const bool pixels = adequate(*service, required);
      if (first < 0 && pixels) {
        first = clock.nsecsElapsed() / 1000000.0;
      }
      if (!service->busy() && (pixels || service->previewErrorKind() != PreviewService::PreviewErrorKind::None)) {
        final = clock.nsecsElapsed() / 1000000.0;
      }
    });
    clock.start();
    observing = true;
    QString error;
    bool success = false;
    if (scenario == "grid-decode") {
#ifdef PREVIEW_DIAGNOSTIC_HEADER
      PreviewEvidence::Context context(PreviewEvidence::consumer, "grid-decode-" + QString::number(index));
      PreviewEvidence::event("consumer_dispatch");
#endif
      const std::atomic_bool cancelled{false};
#ifdef ISOLATED
      const auto decoded = decodeThumbnail({.path = path, .box_pixels = 128}, cancelled, {runtime});
#else
      const auto decoded = decodeThumbnail({.path = path, .box_pixels = 128}, cancelled);
#endif
      success = !decoded.image.isNull();
      error = decoded.error;
      first = success ? clock.nsecsElapsed() / 1000000.0 : -1;
      final = clock.nsecsElapsed() / 1000000.0;
    } else {
      if (scenario == "burst") {
        observing = false;
        for (int selection = 0; selection < 20; ++selection) {
          target(*service, paths[count + selection]);
        }
        observing = true;
      }
      if (scenario == "upgrade") {
        service->setQuickLookActive(true);
      } else {
        target(*service, path);
      }
      success = settle(*service, required);
      error = service->previewErrorMessage();
    }
    observing = false;
    QObject::disconnect(connection);
    const double wall = clock.nsecsElapsed() / 1000000.0;
    // For small images already adequate at pane size, activation needs no job.
    if (scenario == "upgrade" && success && final < 0) {
      first = final = wall;
    }
    const bool correctPixels = scenario == "grid-decode" || service->image() == expected.image;
    const bool correctMetadata =
        scenario == "grid-decode" ||
        (service->sourcePixelSize() == inspection.orientedSize && service->exifMake() == sourceFacts.make &&
         service->exifModel() == sourceFacts.model && service->exifLensModel() == sourceFacts.lens);
    success = success && correctPixels && correctMetadata;
    samples.append(QJsonObject{{"correct_pixels", correctPixels},
                               {"correct_metadata", correctMetadata},
                               {"cleanup_failure", cleanupFailure.load()},
                               {"delivered_width", service->image().width()},
                               {"delivered_height", service->image().height()},
                               {"required_width", required.width()},
                               {"required_height", required.height()},
                               {"first_ms", first},
                               {"final_ms", final},
                               {"wall_ms", wall},
                               {"success", success},
                               {"setup_success", setupOk},
                               {"error", error},
                               {"harness_timeout", service->busy()},
                               {"superseded_selections", scenario == "burst" ? 20 : 0}});
    service->clear();
    if (cleanupFailure.load() || !success) {
      break;
    }
#ifdef PREVIEW_DIAGNOSTIC_HEADER
    PreviewEvidence::event("sample_completed", {{"index", index}, {"scenario", scenario}});
    if (PreviewEvidence::cleanupFailed.load()) break;
#endif
  }
  service.reset();
#ifdef PREVIEW_DIAGNOSTIC_HEADER
  QThread::sleep(1);
  QFile status("/proc/self/status");
  const bool statusAvailable = status.open(QIODevice::ReadOnly);
  PreviewEvidence::event(
      "post_drain_settled",
      {{"parent_status", statusAvailable ? QString::fromUtf8(status.readAll()) : QString{}}, {"settling_ms", 1000}});
  PreviewEvidence::settledScopes();
  PreviewEvidence::buffer.flush();
#endif
  rusage parent{};
  rusage children{};
  getrusage(RUSAGE_SELF, &parent);
  getrusage(RUSAGE_CHILDREN, &children);
  QJsonObject result{{"scenario", scenario},
                     {"fixture", fixture},
                     {"samples", samples},
                     {"parent_maxrss_kib", double(parent.ru_maxrss)},
                     {"parent_cpu_ms", cpu(parent)},
                     {"reaped_children_cpu_ms", cpu(children)},
                     {"reaped_children_maxrss_kib", double(children.ru_maxrss)},
                     {"worker_readiness", "not-applicable: no prestarted worker in A/B"}};
  QFile output(QString::fromLocal8Bit(argv[5]));
  if (!output.open(QIODevice::WriteOnly | QIODevice::NewOnly)) {
    return 5;
  }
  const auto bytes = QJsonDocument(result).toJson();
  if (output.write(bytes) != bytes.size() || !output.flush()) return 6;
#ifdef PREVIEW_DIAGNOSTIC_HEADER
  if (PreviewEvidence::cleanupFailed.load()) return 20;
#endif
  return cleanupFailure.load() ? 20 : 0;
}
