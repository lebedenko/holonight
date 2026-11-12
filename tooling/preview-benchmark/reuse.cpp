// SPDX-License-Identifier: GPL-3.0-or-later
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QTemporaryDir>
#include <QThread>

#include <HolonightFileBrowser/preview/image_policy.h>
#include <HolonightFileBrowser/preview/preview_service.h>
#include <atomic>
#include <holonight_thumbnails/cache.h>
#include <memory>
#include <semaphore>
#include <sys/resource.h>
#include <sys/stat.h>

// The same existing seam is used in every variant. Cancellation setup stops
// after helper inspection, proving a dispatched transaction before
// cancellation.
struct PreviewServiceTestAccess {
  static bool ready(const PreviewService& service) {
#ifdef REUSABLE_VARIANT
    return service.runtime_ready_for_test_.load();
#else
    return !service.active_job_;
#endif
  }
  static void beforeDecode(PreviewService& service, std::function<void()> callback) {
    service.before_full_decode_for_test_ = std::move(callback);
  }
};
namespace {
std::atomic_bool cleanup_failure{false};
void messages(QtMsgType, const QMessageLogContext&, const QString& message) {
  if (message.startsWith("Preview runtime failure 4")) {
    cleanup_failure.store(true);
  }
  std::fprintf(stderr, "%s\n", qPrintable(message));
}
void target(PreviewService& service, const QString& path) {
  service.setTarget(path, false, 0, {}, S_IFREG | 0600, false, {});
}
void events() {
  QCoreApplication::processEvents();
  QThread::usleep(100);
}
bool settle(PreviewService& service) {
  QElapsedTimer deadline;
  deadline.start();
  while (service.busy() && deadline.elapsed() < 10000) {
    events();
  }
  return !service.busy() && service.hasImage() && service.previewErrorKind() == PreviewService::PreviewErrorKind::None;
}
bool ready(PreviewService& service) {
  QElapsedTimer deadline;
  deadline.start();
  while (!PreviewServiceTestAccess::ready(service) && deadline.elapsed() < 10000) {
    events();
  }
  return PreviewServiceTestAccess::ready(service);
}
double cpu(const rusage& value) {
  return value.ru_utime.tv_sec * 1000.0 + value.ru_utime.tv_usec / 1000.0 + value.ru_stime.tv_sec * 1000.0 +
         value.ru_stime.tv_usec / 1000.0;
}
}  // namespace
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  qInstallMessageHandler(messages);
  if (argc != 6) {
    return 2;
  }
  const QString runtime = QString::fromLocal8Bit(argv[1]);
  const QString fixture = QString::fromLocal8Bit(argv[2]);
  const QString scenario = QString::fromLocal8Bit(argv[3]);
  bool parsed = false;
  const int count = QString::fromLocal8Bit(argv[4]).toInt(&parsed);
  const QStringList scenarios{
      "ready",        "disk",          "memory",         "startup",       "recycle", "cancel-depletion",
      "navigation-0", "navigation-25", "navigation-100", "navigation-250"};
  if (!parsed || count < 1 || count > 1000 || !scenarios.contains(scenario)) {
    return 2;
  }
  QTemporaryDir directory;
  if (!directory.isValid()) {
    return 3;
  }
  qputenv("XDG_CACHE_HOME", QFile::encodeName(directory.filePath("cache")));
  QFile reference(fixture);
  if (!reference.open(QIODevice::ReadOnly)) {
    return 4;
  }
  const std::atomic_bool cancelled{false};
  const auto inspection = HolonightImages::inspect(reference, kPreviewImageLimits, cancelled);
  const auto required = ThumbnailService::requiredSize(inspection.orientedSize, {256, 256});
  const auto tier = ThumbnailService::tierForSize(required);
  const auto bound = tier ? QSize(static_cast<int>(*tier), static_cast<int>(*tier)) : QSize(256, 256);
  const auto expected = HolonightImages::decode(reference, {.limits = kPreviewImageLimits, .bound = bound}, cancelled);
  if (expected.outcome != HolonightImages::Outcome::Success) {
    return 4;
  }
  QStringList paths;
  // Unique sources force session work; private files avoid historical cache
  // hits.
  for (int number = 0; number < count * 8 + 8; ++number) {
    const auto path = directory.filePath(QString::number(number) + '.' + fixture.section('.', -1));
    if (!QFile::copy(fixture, path)) {
      return 4;
    }
    paths.append(path);
  }
  auto make = [&] {
    auto service = std::make_unique<PreviewService>(HolonightFileBrowser::ImageRuntimeOptions{runtime});
    service->setRequestedSize(PreviewService::PreviewConsumer::Pane, {256, 256});
    return service;
  };
  auto service = make();
  QJsonArray samples;
  bool previous_failure = false;
  constexpr int intermediate = 4;
  for (int number = 0; number < count; ++number) {
    if (previous_failure) {
      samples.append(QJsonObject{{"success", false}, {"missing", true}, {"reason", "earlier failure in block"}});
      continue;
    }
    const auto path = paths[number * 8];
    bool setup = true;
    if (scenario != "startup") {
      if (scenario == "disk" || scenario == "memory") {
        target(*service, path);
        setup = settle(*service) && ready(*service);
        if (scenario == "disk") {
          setup = setup && tier &&
                  QFileInfo::exists(HolonightThumbnails::cachePath(QUrl::fromLocalFile(path), static_cast<int>(*tier)));
        }
        service->clear();
      }
      if (scenario == "disk") {
        service.reset();
        service = make();
      }
      if (scenario != "memory") {
        target(*service, paths[number * 8 + 7]);
        setup = settle(*service) && ready(*service) && setup;
        service->clear();
      }
      if (scenario == "recycle") {
        // 32 started transactions, including the readiness warm-up. Three
        // identities prevent the two-entry memory cache from bypassing workers.
#ifdef REUSABLE_VARIANT
        constexpr int cycle = 32;
#else
        // One-shot variants have no worker to deplete. Four cycling sources give
        // the same disk entries and final two-entry LRU order as 31 transactions.
        constexpr int cycle = 5;
#endif
        for (int transaction = 1; transaction < cycle && setup; ++transaction) {
          target(*service, paths[paths.size() - 2 - transaction % 3]);
          setup = settle(*service) && (transaction + 1 == cycle || ready(*service));
          service->clear();
        }
      }
      if (scenario == "cancel-depletion") {
        for (int depleted = 1; depleted <= 2 && setup; ++depleted) {
          auto reached = std::make_shared<std::binary_semaphore>(0);
          auto release = std::make_shared<std::binary_semaphore>(0);
          PreviewServiceTestAccess::beforeDecode(*service, [reached, release] {
            reached->release();
            release->acquire();
          });
          target(*service, paths[number * 8 + depleted]);
          QElapsedTimer deadline;
          deadline.start();
          bool dispatched = false;
          while (!(dispatched = reached->try_acquire()) && deadline.elapsed() < 10000) {
            events();
          }
          setup = dispatched;
          service->clear();
          PreviewServiceTestAccess::beforeDecode(*service, {});
          release->release();
          // The next source inspection starts only after cancellation cleanup.
        }
      }
    } else {
      service.reset();
    }
    if (!setup || cleanup_failure.load()) {
      samples.append(
          QJsonObject{{"success", false}, {"setup_success", setup}, {"cleanup_failure", cleanup_failure.load()}});
      previous_failure = true;
      continue;
    }
    QElapsedTimer clock;
    clock.start();
    if (scenario == "startup") {
      service = make();
    }
    const bool navigation = scenario.startsWith("navigation-");
    int selection = navigation ? 0 : intermediate;
    qint64 selected_at = scenario == "startup" ? 0 : clock.nsecsElapsed();
    double pixels = -1;
    double metadata = -1;
    QJsonArray deliveries;
    bool pixel_delivered = false;
    bool final_delivered = false;
    const auto connection = QObject::connect(service.get(), &PreviewService::changed, &app, [&] {
      const auto latency = (clock.nsecsElapsed() - selected_at) / 1000000.0;
      const bool adequate = service->hasImage() && service->image().width() >= required.width() &&
                            service->image().height() >= required.height();
      if (adequate && !pixel_delivered) {
        deliveries.append(QJsonObject{{"selection", selection}, {"event", "pixels"}, {"latency_ms", latency}});
        pixel_delivered = true;
        if (selection == intermediate) {
          pixels = latency;
        }
      }
      if (!service->busy() && !final_delivered &&
          (adequate || service->previewErrorKind() != PreviewService::PreviewErrorKind::None)) {
        deliveries.append(QJsonObject{{"selection", selection}, {"event", "metadata"}, {"latency_ms", latency}});
        final_delivered = true;
        if (selection == intermediate) {
          metadata = latency;
        }
      }
    });
    if (navigation) {
      const auto interval = scenario.section('-', -1).toInt();
      for (selection = 0; selection < intermediate; ++selection) {
        pixel_delivered = final_delivered = false;
        selected_at = clock.nsecsElapsed();
        target(*service, paths[number * 8 + selection + 1]);
        while ((clock.nsecsElapsed() - selected_at) / 1000000.0 < interval) {
          events();
        }
      }
    }
    pixel_delivered = final_delivered = false;
    if (scenario != "startup") {
      selected_at = clock.nsecsElapsed();
    }
    target(*service, path);
    bool success = settle(*service);
    QObject::disconnect(connection);
    const auto& facts = inspection.metadata.facts;
    const bool correct_pixels = service->image() == expected.image;
    const bool correct_metadata = service->sourcePixelSize() == inspection.orientedSize &&
                                  service->exifMake() == facts.make && service->exifModel() == facts.model &&
                                  service->exifLensModel() == facts.lens;
    success =
        success && correct_pixels && correct_metadata && pixels >= 0 && metadata >= pixels && !cleanup_failure.load();
    samples.append(QJsonObject{{"first_ms", pixels},
                               {"final_ms", metadata},
                               {"success", success},
                               {"setup_success", setup},
                               {"correct_pixels", correct_pixels},
                               {"correct_metadata", correct_metadata},
                               {"cleanup_failure", cleanup_failure.load()},
                               {"harness_timeout", service->busy()},
                               {"error", service->previewErrorMessage()},
                               {"deliveries", deliveries},
                               {"superseded_selections", navigation ? intermediate : 0}});
    service->clear();
    previous_failure = !success;
  }
  service.reset();
  rusage parent{}, children{};
  getrusage(RUSAGE_SELF, &parent);
  getrusage(RUSAGE_CHILDREN, &children);
  QFile output(QString::fromLocal8Bit(argv[5]));
  if (!output.open(QIODevice::WriteOnly | QIODevice::NewOnly)) {
    return 5;
  }
  const auto bytes = QJsonDocument(QJsonObject{{"scenario", scenario},
                                               {"fixture", fixture},
                                               {"samples", samples},
                                               {"cleanup_failure", cleanup_failure.load()},
                                               {"parent_cpu_ms", cpu(parent)},
                                               {"children_cpu_ms", cpu(children)},
                                               {"parent_maxrss_kib", double(parent.ru_maxrss)},
                                               {"navigation_intermediate_selections", intermediate}})
                         .toJson();
  if (output.write(bytes) != bytes.size() || !output.flush()) {
    return 6;
  }
  return previous_failure || cleanup_failure.load() ? 20 : 0;
}
