#include <QColorSpace>
#include <QCoreApplication>
#include <QCryptographicHash>
#include <QElapsedTimer>
#include <QFile>
#include <QImageWriter>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QBuffer>
#include <holonight_images/image.h>
#define HolonightThumbnails Store_default
#include <holonight_thumbnails/cache.h>
#undef HolonightThumbnails
#include "../sources/11/store.h"
#include "../sources/0/store.h"

static void require(bool okay) { if (!okay) std::abort(); }
static QByteArray pixels(const QImage& image) {
  auto rgba = image.convertToFormat(QImage::Format_RGBA8888);
  return QCryptographicHash::hash(QByteArrayView(reinterpret_cast<const char*>(rgba.constBits()), rgba.sizeInBytes()), QCryptographicHash::Sha256).toHex();
}
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  if (argc == 2 && QByteArray(argv[1]) == "mapping") {
    for (int setting : {11, 0}) {
      QByteArray bytes;
      QBuffer buffer(&bytes);
      require(buffer.open(QIODevice::WriteOnly));
      QImageWriter writer(&buffer, "PNG");
      require(writer.supportsOption(QImageIOHandler::CompressionRatio));
      writer.setCompression(setting);
      QImage image(8, 8, QImage::Format_RGBA8888); image.fill(Qt::red);
      require(writer.write(image));
    }
    return 0;
  }
  require(argc == 3);
  const QString directory = QString::fromLocal8Bit(argv[1]);
  const std::atomic_bool cancelled{false};
  QJsonArray rows, corpus;
  for (const QString name : {QString("textured"), QString("flat"), QString("alpha"), QString("oriented")}) {
    for (int tier : {128, 256, 512, 1024}) {
      QImage image;
      if (name == "flat" || name == "alpha") {
        QImage source(3200, 2400, QImage::Format_RGBA8888);
        source.setColorSpace(QColorSpace::SRgb);
        source.fill(QColor(31, 83, 149, 255));
        if (name == "alpha") {
          for (int y = 0; y < source.height(); ++y)
            for (int x = 0; x < source.width(); ++x)
              source.setPixelColor(x, y, QColor((x * 13 + y * 3) % 256, (x + y * 7) % 256, (x * 5 + y) % 256, (x + y * 3) % 256));
        }
        // PNG decode uses this same bounded size and smooth fallback policy.
        image = source.scaled(QSize(tier, tier), Qt::KeepAspectRatio, Qt::SmoothTransformation);
      } else {
        QFile source(directory + (name == "textured" ? "/textured.png" : "/oriented.jpg"));
        require(source.open(QIODevice::ReadOnly));
        auto result = HolonightImages::decode(source, {{256LL*1024*1024, 100000000, 32768, 512LL*1024*1024, 8*1024*1024, 8*1024*1024, 10000}, QSize(tier,tier), HolonightImages::OrientationPolicy::Apply}, cancelled);
        require(result.outcome == HolonightImages::Outcome::Success);
        image = result.image;
      }
      require(!image.isNull());
      const QString id = name + '-' + QString::number(tier);
      // Exactly identical source metadata and cache key for all modes and observations.
      Store_default::Request request{QUrl::fromLocalFile(directory + "/source-" + name), QDateTime::fromMSecsSinceEpoch(1700000000123LL), 1234567, image.size(), Store_default::Kind::Raster, "encoding-trial-v1", tier};
      Store_11::Request request11{request.uri, request.modified, request.size, request.required, Store_11::Kind::Raster, request.revision, tier};
      Store_0::Request request0{request.uri, request.modified, request.size, request.required, Store_0::Kind::Raster, request.revision, tier};
      const auto path = Store_default::cachePath(request.uri, tier);
      corpus.append(QJsonObject{{"id",id},{"tier",tier},{"width",image.width()},{"height",image.height()},{"pixels",QString(pixels(image))},{"alpha",image.hasAlphaChannel()},{"icc",QString(QCryptographicHash::hash(image.colorSpace().iccProfile(), QCryptographicHash::Sha256).toHex())}});
      auto store = [&](int mode, bool warmup, int block, int observation) {
        QElapsedTimer timer; timer.start();
        bool okay = mode == 0 ? Store_default::store(request,image,cancelled,{}) : mode == 1 ? Store_11::store(request11,image,cancelled,{}) : Store_0::store(request0,image,cancelled,{});
        auto ns = timer.nsecsElapsed();
        require(okay);
        QFile file(path); require(file.open(QIODevice::ReadOnly));
        const auto bytes = file.readAll();
        QImage decoded; require(decoded.loadFromData(bytes,"PNG"));
        QJsonObject texts;
        for (auto key : decoded.textKeys()) texts[key] = decoded.text(key);
        require(pixels(image) == pixels(decoded) && image.hasAlphaChannel() == decoded.hasAlphaChannel() && image.colorSpace() == decoded.colorSpace());
        rows.append(QJsonObject{{"id",id},{"mode",mode == 0 ? "default" : mode == 1 ? "11" : "0"},{"warmup",warmup},{"block",block},{"observation",observation},{"ns",ns},{"bytes",bytes.size()},{"sha256",QString(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex())},{"pixels",QString(pixels(decoded))},{"alpha",decoded.hasAlphaChannel()},{"icc",QString(QCryptographicHash::hash(decoded.colorSpace().iccProfile(),QCryptographicHash::Sha256).toHex())},{"metadata",texts}});
        // Retain each mode's exact bytes for independent decoding, outside timing.
        QFile retained(directory + '/' + id + '-' + (mode == 0 ? "default" : mode == 1 ? "11" : "0") + ".png");
        require(retained.open(QIODevice::WriteOnly)); require(retained.write(bytes) == bytes.size());
      };
      for (int mode=0; mode<3; ++mode) store(mode,true,-1,0);
      for (int block=0; block<6; ++block)
        for (int offset=0; offset<3; ++offset)
          for (int observation=0; observation<5; ++observation) store((block+offset)%3,false,block,observation);
    }
  }
  QFile output(QString::fromLocal8Bit(argv[2])); require(output.open(QIODevice::WriteOnly | QIODevice::NewOnly));
  require(output.write(QJsonDocument(QJsonObject{{"qt",qVersion()},{"corpus",corpus},{"rows",rows}}).toJson()) > 0);
  return 0;
}
