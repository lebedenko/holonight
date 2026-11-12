// SPDX-License-Identifier: GPL-3.0-or-later
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTemporaryDir>
#include <QThread>

#include <HolonightFileBrowser/preview/preview_service.h>
#include <cstdio>
#include <memory>
#include <sys/stat.h>

namespace {
void event(const char* phase, int selection = -1) {
  const auto bytes =
      QJsonDocument(QJsonObject{{"phase", phase}, {"selection", selection}}).toJson(QJsonDocument::Compact);
  std::fwrite(bytes.constData(), 1, bytes.size(), stdout);
  std::fputc('\n', stdout);
  std::fflush(stdout);
}
void pump() {
  QCoreApplication::processEvents();
  QThread::msleep(1);
}
void wait(int milliseconds) {
  QElapsedTimer clock;
  clock.start();
  while (clock.elapsed() < milliseconds) {
    pump();
  }
}
void target(PreviewService& service, const QString& path) {
  service.setTarget(path, false, 0, {}, S_IFREG | 0600, false, {});
}
bool settle(PreviewService& service) {
  QElapsedTimer clock;
  clock.start();
  while (service.busy() && clock.elapsed() < 10000) {
    pump();
  }
  return !service.busy() && service.hasImage() && service.previewErrorKind() == PreviewService::PreviewErrorKind::None;
}
}  // namespace
// Resource diagnostics only. Never use these instrumented observations as
// latency samples. A single service survives count and age recycling, idle
// expiry, an adequate memory hit, renewed demand and final shutdown.
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  if (argc != 3) {
    return 2;
  }
  QTemporaryDir directory;
  if (!directory.isValid()) {
    return 3;
  }
  qputenv("XDG_CACHE_HOME", QFile::encodeName(directory.filePath("cache")));
  QStringList paths;
  for (int number = 0; number < 4; ++number) {
    const auto path = directory.filePath(QString::number(number) + ".png");
    if (!QFile::copy(QString::fromLocal8Bit(argv[2]), path)) {
      return 4;
    }
    paths.append(path);
  }
  event("construct");
  auto service =
      std::make_unique<PreviewService>(HolonightFileBrowser::ImageRuntimeOptions{QString::fromLocal8Bit(argv[1])});
  service->setRequestedSize(PreviewService::PreviewConsumer::Pane, {256, 256});
  int deliveries = 0;
  const auto changed = QObject::connect(service.get(), &PreviewService::changed, &app, [&] {
    if (!service->busy() && service->hasImage()) {
      ++deliveries;
    }
  });
  // Eighty seconds crosses the 60-second age bound. Three identities exceed
  // the two-entry memory cache, so sustained demand keeps exercising sessions.
  QElapsedTimer clock;
  clock.start();
  int selection = 0;
  for (; selection < 320; ++selection) {
    event("navigation", selection);
    target(*service, paths[selection % 3]);
    const auto next = (selection + 1) * 250;
    while (clock.elapsed() < next) {
      pump();
    }
  }
  if (!settle(*service) || deliveries == 0) {
    event("failure");
    return 20;
  }
  QObject::disconnect(changed);
  const auto expected = service->image();
  event("idle");
  wait(35000);
  event("memory-hit");
  service->clear();
  target(*service, paths[(selection - 1) % 3]);
  if (!settle(*service) || service->image() != expected) {
    event("failure");
    return 20;
  }
  wait(1000);
  event("renewed-demand");
  target(*service, paths[3]);
  if (!settle(*service) || service->image() != expected) {
    event("failure");
    return 20;
  }
  event("shutdown");
  service.reset();
  event("finished");
  return 0;
}
