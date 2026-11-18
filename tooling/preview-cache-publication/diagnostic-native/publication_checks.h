#pragma once
#include <HolonightFileBrowser/preview/preview_service.h>
#include <holonight_thumbnails/cache.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonObject>
#include <atomic>

// Additional evidence is collected only after final delivery, outside the
// overlap interval.
struct PublicationChecks {
  QJsonObject record;
  void finish(const PreviewService& service, const QString& path, const QString& runtime, int tier,
              QSize required) {
    struct timespec stamp{};
    clock_gettime(CLOCK_MONOTONIC, &stamp);
    struct stat info{};
    if (::stat(QFile::encodeName(path).constData(), &info) != 0) return;
    const auto identity = QStringLiteral("%1:%2:%3:%4:%5:%6:%7")
                              .arg(info.st_dev)
                              .arg(info.st_ino)
                              .arg(info.st_size)
                              .arg(info.st_mtim.tv_sec)
                              .arg(info.st_mtim.tv_nsec)
                              .arg(info.st_ctim.tv_sec)
                              .arg(info.st_ctim.tv_nsec);
    QFile input(path);
    if (!input.open(QIODevice::ReadOnly)) return;
    const auto sourceHash = QCryptographicHash::hash(input.readAll(), QCryptographicHash::Sha256).toHex();
    const auto uri = QUrl::fromLocalFile(path);
    const std::atomic_bool cancelled{false};
    const auto cached =
        HolonightThumbnails::lookup({.uri = uri,
                                     .modified = QDateTime::fromMSecsSinceEpoch(
                                         qint64(info.st_mtim.tv_sec) * 1000 + info.st_mtim.tv_nsec / 1000000),
                                     .size = info.st_size,
                                     .required = required,
                                     .kind = HolonightThumbnails::Kind::Raster,
                                     .revision = identity,
                                     .tier = tier},
                                    cancelled);
    const auto cachePath = HolonightThumbnails::cachePath(uri, tier);
    QFile cache(cachePath);
    const bool readable = cache.open(QIODevice::ReadOnly);
    const auto cacheHash = readable
                               ? QCryptographicHash::hash(cache.readAll(), QCryptographicHash::Sha256).toHex()
                               : QByteArray{};
    const auto evidence = qEnvironmentVariable("PUBLICATION_EVIDENCE");
    const bool copied =
        QFile::copy(path, evidence + "/source.png") && QFile::copy(cachePath, evidence + "/cache.png");
    QFile selector(runtime + "/current");
    const auto selected =
        selector.open(QIODevice::ReadOnly) ? QString::fromUtf8(selector.readAll()).trimmed() : QString{};
    const auto generation = runtime + "/generations/" + selected;
    QJsonObject lease;
    const QDir descriptors("/proc/self/fd");
    for (const auto& descriptor : descriptors.entryList(QDir::AllEntries | QDir::NoDotAndDotDot)) {
      const auto fdPath = descriptors.filePath(descriptor);
      if (QFileInfo(fdPath).symLinkTarget() != generation) continue;
      struct stat held{};
      if (::stat(QFile::encodeName(fdPath).constData(), &held) != 0) continue;
      QFile fdinfo("/proc/self/fdinfo/" + descriptor);
      if (!fdinfo.open(QIODevice::ReadOnly)) continue;
      const auto details = QString::fromUtf8(fdinfo.readAll());
      if (!details.contains("FLOCK  ADVISORY  READ") && !details.contains("FLOCK ADVISORY READ")) continue;
      lease = {{"target", generation},
               {"device", QString::number(held.st_dev)},
               {"inode", QString::number(held.st_ino)},
               {"fdinfo", details}};
      break;
    }
    record = {{"source_identity", identity},
              {"source_path", path},
              {"source_sha256", QString::fromLatin1(sourceHash)},
              {"cache_sha256", QString::fromLatin1(cacheHash)},
              {"cache_path", cachePath},
              {"cache_available_at_final", cached.has_value()},
              {"cache_pixels_match", cached && *cached == service.image()},
              {"copied", copied},
              {"check_ns", QString::number(qint64(stamp.tv_sec) * 1000000000 + stamp.tv_nsec)},
              {"selected_generation", selected},
              {"lease", lease}};
  }
};

inline QString publicationMaps() {
  QFile maps("/proc/self/maps");
  return maps.open(QIODevice::ReadOnly) ? QString::fromUtf8(maps.readAll()) : QString{};
}
