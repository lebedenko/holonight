// SPDX-License-Identifier: GPL-3.0-or-later
#include <QCoreApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QSignalSpy>
#include <QThread>

#include <cstdio>
#include <mutex>
#include FROZEN_PREVIEW_TEST

namespace {
std::mutex messagesMutex;
QList<QJsonObject> messages;
QtMessageHandler previousHandler = nullptr;
void capture(QtMsgType type, const QMessageLogContext& context, const QString& message) {
  if (message.startsWith("CACHE_PUBLICATION ")) {
    const std::lock_guard lock(messagesMutex);
    messages.append(QJsonDocument::fromJson(message.mid(18).toUtf8()).object());
  }
  if (previousHandler) {
    previousHandler(type, context, message);
  } else {
    std::fprintf(stderr, "%s\n", message.toLocal8Bit().constData());
  }
}
QString runtime() { return qEnvironmentVariable("PUBLICATION_RUNTIME"); }
QString makeSource(QTemporaryDir& directory, QString name, QColor color) {
  const auto path = directory.filePath(name);
  QImage image(80, 40, QImage::Format_RGB32);
  image.fill(color);
  return image.save(path) ? path : QString{};
}
QString orientedSource(QTemporaryDir& directory) {
  QFile source(QDir(QString::fromUtf8(BROWSER_TEST_FIXTURES)).filePath("sample.jpg"));
  if (!source.open(QIODevice::ReadOnly)) {
    return {};
  }
  auto bytes = source.readAll();
  const auto oldExif = QByteArray::fromHex(
      "ffe1002245786966000049492a00080000000100120103000100"
      "00000600000000000000");
  const auto newExif = QByteArray::fromHex(
      "ffe1002e45786966000049492a00080000000200120103000100"
      "0000060000000f0102000400000043616d0000000000");
  if (!bytes.contains(oldExif)) {
    return {};
  }
  bytes.replace(oldExif, newExif);
  QFile target(directory.filePath("oriented.jpg"));
  if (!target.open(QIODevice::WriteOnly) || target.write(bytes) != bytes.size()) {
    return {};
  }
  return target.fileName();
}
void select(PreviewService& service, const QString& path) {
  service.setRequestedSize(PreviewService::PreviewConsumer::Pane, {256, 256});
  service.setTarget(path, false, 0, {}, S_IFREG | 0600, false, {}, {});
}
void finish(PreviewService& service, QSignalSpy& stopped) {
  service.shutdown();
  EXPECT_TRUE(QTest::qWaitFor([&] { return !stopped.isEmpty(); }, 5000));
  QCoreApplication::processEvents();
}
}  // namespace

TEST(Publication, ProgressivePixelsFinalMetadataAndContext) {
  QTemporaryDir directory;
  ASSERT_TRUE(directory.isValid());
  const auto path = orientedSource(directory);
  ASSERT_FALSE(path.isEmpty());
  QSemaphore reached;
  QSemaphore resume;
  bool progressive = false;
  bool final = false;
  QJsonObject firstContext;
  QJsonObject finalContext;
  PreviewService service({runtime()});
  QSignalSpy stopped(&service, &PreviewService::shutdownFinished);
  const auto release = qScopeGuard([&] {
    resume.release();
    finish(service, stopped);
  });
  PreviewServiceTestAccess::stage(service, [&](ThumbnailService::Stage stage) {
    if (stage == ThumbnailService::Stage::BeforeCommit) {
      reached.release();
      resume.acquire();
    }
  });
  QObject::connect(&service, &PreviewService::changed, &service, [&] {
    if (service.hasImage() && service.busy()) {
      progressive = true;
      firstContext = QThread::currentThread()->property("cachePublicationDelivery").toJsonObject();
      EXPECT_EQ(service.image().size(), QSize(20, 40));
      EXPECT_TRUE(service.exifMake().isEmpty());
    }
    if (service.hasImage() && !service.busy()) {
      final = true;
      finalContext = QThread::currentThread()->property("cachePublicationDelivery").toJsonObject();
      EXPECT_EQ(service.sourcePixelSize(), QSize(20, 40));
      EXPECT_EQ(service.exifMake(), "Cam");
      EXPECT_EQ(service.previewErrorKind(), PreviewService::PreviewErrorKind::None);
      EXPECT_TRUE(QFileInfo::exists(HolonightThumbnails::cachePath(QUrl::fromLocalFile(path), 128)));
    }
  });
  select(service, path);
  ASSERT_TRUE(QTest::qWaitFor([&] { return reached.available() > 0; }, 5000));
  QCoreApplication::processEvents();
  EXPECT_EQ(progressive, qEnvironmentVariable("PUBLICATION_ARM") == "early");
  EXPECT_FALSE(final);
  resume.release();
  ASSERT_TRUE(QTest::qWaitFor([&] { return final; }, 5000));
  EXPECT_TRUE(progressive);
  for (const auto* key : {"invocation", "service", "request", "worker", "preparation", "transaction"}) {
    EXPECT_FALSE(firstContext.value(key).toString().isEmpty()) << key;
  }
  EXPECT_EQ(firstContext.value("invocation").toString(), qEnvironmentVariable("HOLONIGHT_CACHE_INVOCATION"));
  EXPECT_EQ(firstContext, finalContext);
  QList<QJsonObject> captured;
  {
    const std::lock_guard lock(messagesMutex);
    captured = messages;
  }
  for (const auto* event : {"eligible", "store_entry", "store_return", "enqueue", "accepted", "final"}) {
    bool found = false;
    for (const auto& row : captured) {
      if (row.value("event") != event || row.value("request") != firstContext.value("request")) {
        continue;
      }
      found = true;
      for (const auto* key : {"invocation", "service", "request", "worker", "preparation", "transaction"}) {
        EXPECT_EQ(row.value(key), firstContext.value(key)) << event << ":" << key;
      }
    }
    EXPECT_TRUE(found) << event;
  }
}

namespace {
enum class Action { Cancel, Supersede, Timeout, Shutdown };
void commitGate(Action action) {
  QTemporaryDir directory;
  ASSERT_TRUE(directory.isValid());
  const auto oldPath = makeSource(directory, "old.png", Qt::red);
  const auto newPath = makeSource(directory, "new.png", Qt::blue);
  ASSERT_FALSE(oldPath.isEmpty());
  ASSERT_FALSE(newPath.isEmpty());
  QSemaphore reached;
  QSemaphore resume;
  bool triggered = false;
  bool stale = false;
  bool replacement = false;
  QImage accepted;
  PreviewService service({runtime()});
  QSignalSpy stopped(&service, &PreviewService::shutdownFinished);
  const auto release = qScopeGuard([&] {
    resume.release();
    finish(service, stopped);
  });
  PreviewServiceTestAccess::stage(service, [&](ThumbnailService::Stage stage) {
    if (stage == ThumbnailService::Stage::BeforeCommit) {
      reached.release();
      resume.acquire();
    }
  });
  QObject::connect(&service, &PreviewService::changed, &service, [&] {
    if (triggered && service.hasImage() && service.image().pixelColor(0, 0) == QColor(Qt::red)) {
      stale = true;
    }
    if (service.hasImage() && !service.busy() && service.image().pixelColor(0, 0) == QColor(Qt::blue)) {
      replacement = true;
    }
  });
  select(service, oldPath);
  ASSERT_TRUE(QTest::qWaitFor([&] { return reached.available() > 0; }, 5000));
  QCoreApplication::processEvents();
  accepted = service.image();
  PreviewServiceTestAccess::stage(service, {});
  if (action == Action::Timeout) {
    ASSERT_TRUE(QTest::qWaitFor(
        [&] { return service.previewErrorKind() == PreviewService::PreviewErrorKind::DecodeTimeout; }, 5000));
    triggered = true;
  } else {
    triggered = true;
    if (action == Action::Cancel) {
      service.clear();
    } else if (action == Action::Supersede) {
      select(service, newPath);
    } else {
      service.shutdown();
      EXPECT_TRUE(stopped.isEmpty());
    }
  }
  resume.release();
  if (action == Action::Supersede) {
    ASSERT_TRUE(QTest::qWaitFor([&] { return replacement; }, 5000));
    EXPECT_EQ(service.image().pixelColor(0, 0), QColor(Qt::blue));
    EXPECT_EQ(service.sourcePixelSize(), QSize(80, 40));
    EXPECT_EQ(service.previewErrorKind(), PreviewService::PreviewErrorKind::None);
  }
  finish(service, stopped);
  EXPECT_FALSE(stale);
  EXPECT_FALSE(QFileInfo::exists(HolonightThumbnails::cachePath(QUrl::fromLocalFile(oldPath), 128)));
  if (action == Action::Shutdown) {
    EXPECT_EQ(service.image(), accepted);
  } else if (action != Action::Supersede) {
    EXPECT_FALSE(service.hasImage());
  }
}
}  // namespace
TEST(Publication, CancellationDuringCommitSuppressesOldApplication) { commitGate(Action::Cancel); }
TEST(Publication, SupersessionDuringCommitCompletesReplacement) { commitGate(Action::Supersede); }
TEST(Publication, TimeoutDuringCommitSuppressesOldApplication) { commitGate(Action::Timeout); }
TEST(Publication, ShutdownDuringCommitFinishesAsynchronously) { commitGate(Action::Shutdown); }

TEST(Publication, StoreFailurePreservesPixelsAndFinalMetadata) {
  QTemporaryDir directory;
  ASSERT_TRUE(directory.isValid());
  const auto path = orientedSource(directory);
  ASSERT_FALSE(path.isEmpty());
  const auto cache = qgetenv("XDG_CACHE_HOME");
  const auto restore = qScopeGuard([&] { qputenv("XDG_CACHE_HOME", cache); });
  QFile blocked(directory.filePath("not-a-directory"));
  ASSERT_TRUE(blocked.open(QIODevice::WriteOnly));
  blocked.close();
  ASSERT_TRUE(qputenv("XDG_CACHE_HOME", QFile::encodeName(blocked.fileName())));
  bool final = false;
  PreviewService service({runtime()});
  QSignalSpy stopped(&service, &PreviewService::shutdownFinished);
  const auto cleanup = qScopeGuard([&] { finish(service, stopped); });
  QObject::connect(&service, &PreviewService::changed, &service,
                   [&] { final |= service.hasImage() && !service.busy(); });
  select(service, path);
  ASSERT_TRUE(QTest::qWaitFor([&] { return final; }, 5000));
  EXPECT_EQ(service.image().size(), QSize(20, 40));
  EXPECT_EQ(service.sourcePixelSize(), QSize(20, 40));
  EXPECT_EQ(service.exifMake(), "Cam");
  EXPECT_EQ(service.previewErrorKind(), PreviewService::PreviewErrorKind::None);
  EXPECT_FALSE(QFileInfo::exists(HolonightThumbnails::cachePath(QUrl::fromLocalFile(path), 128)));
}

int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  if (qEnvironmentVariableIsEmpty("HOLONIGHT_CACHE_INVOCATION") || runtime().isEmpty() ||
      qEnvironmentVariableIsEmpty("XDG_CACHE_HOME") || qEnvironmentVariableIsEmpty("TMPDIR")) {
    return 2;
  }
  previousHandler = qInstallMessageHandler(capture);
  const auto restore = qScopeGuard([] { qInstallMessageHandler(previousHandler); });
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
