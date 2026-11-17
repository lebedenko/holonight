// SPDX-License-Identifier: GPL-3.0-or-later
#include <QCoreApplication>
#include <QJsonObject>
#include <QThread>
#include <thread>
#include FROZEN_PREVIEW_TEST

namespace {
QString makeSource(QTemporaryDir& directory, QString name, QColor color) {
  const auto path = directory.filePath(name);
  QImage image(80, 40, QImage::Format_RGB32);
  image.fill(color);
  if (!image.save(path)) {
    return {};
  }
  return path;
}
void select(PreviewService& service, const QString& path) {
  service.setRequestedSize(PreviewService::PreviewConsumer::Pane, {256, 256});
  service.setTarget(path, false, 0, {}, S_IFREG | 0600, false, {}, {});
}
}  // namespace

TEST(Publication, ProgressivePixelsFinalMetadataAndContext) {
  QTemporaryDir directory;
  ASSERT_TRUE(directory.isValid());
  const auto path = makeSource(directory, "ordering.png", Qt::red);
  ASSERT_FALSE(path.isEmpty());
  PreviewService service({QString::fromUtf8(BROWSER_TEST_RUNTIME)});
  QSemaphore reached;
  QSemaphore resume;
  const auto release = qScopeGuard([&] { resume.release(); });
  PreviewServiceTestAccess::stage(service, [&](ThumbnailService::Stage stage) {
    if (stage == ThumbnailService::Stage::BeforeCommit) {
      reached.release();
      resume.acquire();
    }
  });
  bool progressive = false;
  bool final = false;
  QJsonObject firstContext;
  QObject::connect(&service, &PreviewService::changed, &service, [&] {
    if (service.hasImage() && service.busy()) {
      progressive = true;
      firstContext = QThread::currentThread()->property("cachePublicationDelivery").toJsonObject();
      EXPECT_EQ(service.image().pixelColor(0, 0), QColor(Qt::red));
    }
    if (service.hasImage() && !service.busy()) {
      final = true;
      EXPECT_EQ(service.sourcePixelSize(), QSize(80, 40));
      EXPECT_TRUE(QFileInfo::exists(HolonightThumbnails::cachePath(QUrl::fromLocalFile(path), 128)));
    }
  });
  select(service, path);
  ASSERT_TRUE(QTest::qWaitFor([&] { return reached.available() > 0; }, 5000));
  QCoreApplication::processEvents();
  if (qEnvironmentVariable("PUBLICATION_ARM") == "early") {
    EXPECT_TRUE(progressive);
  } else {
    EXPECT_FALSE(progressive);
  }
  EXPECT_FALSE(final);
  resume.release();
  ASSERT_TRUE(QTest::qWaitFor([&] { return !service.busy(); }, 5000));
  EXPECT_TRUE(progressive);
  EXPECT_TRUE(final);
  for (const auto* key : {"invocation", "service", "request", "worker", "preparation", "transaction"}) {
    EXPECT_FALSE(firstContext.value(key).toString().isEmpty()) << key;
  }
  EXPECT_EQ(firstContext.value("invocation").toString(), qEnvironmentVariable("HOLONIGHT_CACHE_INVOCATION"));
  const auto finalContext = QThread::currentThread()->property("cachePublicationDelivery").toJsonObject();
  EXPECT_EQ(firstContext, finalContext);
  service.shutdown();
}

TEST(Publication, CommitBarrierRejectsCancelledSupersededTimedOutAndShutdownResults) {
  for (int action = 0; action < 4; ++action) {
    SCOPED_TRACE(action);
    QTemporaryDir directory;
    ASSERT_TRUE(directory.isValid());
    const auto oldPath = makeSource(directory, "old.png", Qt::red);
    const auto newPath = makeSource(directory, "new.png", Qt::blue);
    PreviewService service({QString::fromUtf8(BROWSER_TEST_RUNTIME)});
    QSemaphore reached;
    QSemaphore resume;
    const auto release = qScopeGuard([&] { resume.release(); });
    PreviewServiceTestAccess::stage(service, [&](ThumbnailService::Stage stage) {
      if (stage == ThumbnailService::Stage::BeforeCommit) {
        reached.release();
        resume.acquire();
      }
    });
    select(service, oldPath);
    ASSERT_TRUE(QTest::qWaitFor([&] { return reached.available() > 0; }, 5000));
    PreviewServiceTestAccess::stage(service, {});
    if (action == 0) {
      service.clear();
    } else if (action == 1) {
      select(service, newPath);
    } else if (action == 2) {
      ASSERT_TRUE(QTest::qWaitFor([&] {
        return service.previewErrorKind() == PreviewService::PreviewErrorKind::DecodeTimeout;
      }, 5000));
    } else {
      // Shutdown waits for the bounded worker. The release is outside that wait.
      std::thread unblock([&] { resume.release(); });
      service.shutdown();
      unblock.join();
    }
    bool stale = false;
    QObject::connect(&service, &PreviewService::changed, &service, [&] {
      stale |= service.hasImage() && service.image().pixelColor(0, 0) == QColor(Qt::red);
    });
    resume.release();
    ASSERT_TRUE(QTest::qWaitFor([&] { return !PreviewServiceTestAccess::active(service); }, 5000));
    EXPECT_FALSE(stale);
    if (action == 1) {
      ASSERT_TRUE(service.hasImage());
      EXPECT_EQ(service.image().pixelColor(0, 0), QColor(Qt::blue));
    } else {
      EXPECT_FALSE(service.hasImage());
    }
    service.shutdown();
  }
}

TEST(Publication, StoreFailurePreservesPixelsAndFinalMetadata) {
  QTemporaryDir directory;
  ASSERT_TRUE(directory.isValid());
  const auto path = makeSource(directory, "failure.png", Qt::red);
  const auto cache = qgetenv("XDG_CACHE_HOME");
  const auto restore = qScopeGuard([&] { qputenv("XDG_CACHE_HOME", cache); });
  QFile blocked(directory.filePath("not-a-directory"));
  ASSERT_TRUE(blocked.open(QIODevice::WriteOnly));
  blocked.close();
  ASSERT_TRUE(qputenv("XDG_CACHE_HOME", QFile::encodeName(blocked.fileName())));
  PreviewService service({QString::fromUtf8(BROWSER_TEST_RUNTIME)});
  select(service, path);
  ASSERT_TRUE(QTest::qWaitFor([&] { return !service.busy(); }, 5000));
  ASSERT_TRUE(service.hasImage());
  EXPECT_EQ(service.image().pixelColor(0, 0), QColor(Qt::red));
  EXPECT_EQ(service.sourcePixelSize(), QSize(80, 40));
  EXPECT_EQ(service.previewErrorKind(), PreviewService::PreviewErrorKind::None);
  EXPECT_FALSE(QFileInfo::exists(HolonightThumbnails::cachePath(QUrl::fromLocalFile(path), 128)));
  service.shutdown();
}

int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  if (qEnvironmentVariableIsEmpty("HOLONIGHT_CACHE_INVOCATION") ||
      qEnvironmentVariableIsEmpty("XDG_CACHE_HOME") || qEnvironmentVariableIsEmpty("TMPDIR")) {
    return 2;
  }
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
