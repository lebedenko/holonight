// SPDX-License-Identifier: GPL-3.0-or-later
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QFile>
#include <QQuickTextureFactory>
#include <QSemaphore>
#include <QTemporaryDir>

#include <HolonightFileBrowser/preview_quick/thumbnail_provider.h>
#include <array>
#include <memory>

namespace {
bool waitFor(const std::function<bool()>& predicate) {
  QElapsedTimer clock;
  clock.start();
  while (!predicate() && clock.elapsed() < 5000) {
    QCoreApplication::processEvents();
    QThread::usleep(100);
  }
  return predicate();
}
}  // namespace
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  QTemporaryDir directory;
  QStringList paths;
  for (int i = 0; i < 16; ++i) {
    paths.append(directory.filePath(QString::number(i)));
    QFile file(paths.last());
    if (!file.open(QIODevice::WriteOnly)) return 1;
    file.write("fixture");
  }
  QSemaphore entered, release;
  std::atomic_int calls{0};
  ThumbnailProvider provider(
      [&](const ThumbnailRequest&, const std::atomic_bool&) {
        const int call = ++calls;
        if (call <= 2) {
          entered.release();
          release.acquire();
        }
        QImage image(8, 8, QImage::Format_ARGB32);
        image.fill(Qt::red);
        return ThumbnailResult{.image = image, .source_size = {8, 8}};
      },
      2);
  std::array<std::unique_ptr<QQuickImageResponse>, 16> responses;
  int finished = 0, images = 0;
  auto issue = [&](int i) {
    responses[i].reset(provider.requestImageResponse(ThumbnailProvider::idFor(paths[i], 256, 0), {}));
    QObject::connect(responses[i].get(), &QQuickImageResponse::finished, &app, [&, i] {
      ++finished;
      std::unique_ptr<QQuickTextureFactory> texture(responses[i]->textureFactory());
      if (texture && texture->image().size() == QSize(8, 8) && texture->image().pixelColor(0, 0) == Qt::red) ++images;
    });
  };
  for (int i = 0; i < 16; ++i) issue(i);
  const bool twoStarted = entered.tryAcquire(2, 5000);
  const bool queued = provider.pendingCount() == 16 && calls == 2;
  for (int i = 0; i < 12; ++i) responses[i]->cancel();
  release.release(2);
  const bool drained = waitFor([&] { return finished == 16 && provider.pendingCount() == 0; });
  if (!twoStarted || !queued || !drained || calls != 6 || images != 4) return 2;
  // Warm requests complete through the response queue without entering the decoder.
  for (int i = 12; i < 16; ++i) issue(i);
  if (!waitFor([&] { return finished == 20; }) || calls != 6 || images != 8 || provider.pendingCount() != 0) return 3;
  // Destroy a response while its decoder is blocked; the provider must still drain.
  QSemaphore lifetimeEntered, lifetimeRelease;
  ThumbnailProvider lifetime(
      [&](const ThumbnailRequest&, const std::atomic_bool&) {
        lifetimeEntered.release();
        lifetimeRelease.acquire();
        return ThumbnailResult{};
      },
      2);
  auto response = std::unique_ptr<QQuickImageResponse>(
      lifetime.requestImageResponse(ThumbnailProvider::idFor(paths[0], 256, 1), {}));
  const bool running = lifetimeEntered.tryAcquire(1, 5000);
  response.reset();
  lifetimeRelease.release();
  if (!waitFor([&] { return lifetime.pendingCount() == 0; }) || !running) return 4;
  QCoreApplication::processEvents();
  return 0;
}
