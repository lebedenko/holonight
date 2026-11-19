// SPDX-License-Identifier: GPL-3.0-or-later
#include <QCoreApplication>
#include <QImage>
#include <QSignalSpy>
#include <QTemporaryDir>
#include <QTest>

#include <HolonightFileBrowser/preview/preview_service.h>
#include <sys/stat.h>
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  QTemporaryDir directory;
  QImage image(80, 40, QImage::Format_RGB32);
  image.fill(Qt::blue);
  const auto path = directory.filePath("consumer.png");
  if (!image.save(path)) {
    return 1;
  }
  PreviewService service({qEnvironmentVariable("PUBLICATION_RUNTIME")});
  QSignalSpy stopped(&service, &PreviewService::shutdownFinished);
  service.setTarget(path, false, 0, {}, S_IFREG | 0600, false, {}, {});
  const bool completed = QTest::qWaitFor([&] { return service.hasImage() && !service.busy(); }, 5000);
  const bool valid = completed && service.image().pixelColor(0, 0) == QColor(Qt::blue) &&
                     service.sourcePixelSize() == QSize(80, 40) &&
                     service.previewErrorKind() == PreviewService::PreviewErrorKind::None;
  service.shutdown();
  return valid && QTest::qWaitFor([&] { return !stopped.isEmpty(); }, 5000) ? 0 : 1;
}
