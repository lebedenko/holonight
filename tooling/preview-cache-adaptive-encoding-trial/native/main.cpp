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
#include "../sources/adaptive/store.h"

#include "detector.h"

static void require(bool okay) { if (!okay) std::abort(); }
static QByteArray pixels(const QImage& image) {
  auto rgba = image.convertToFormat(QImage::Format_RGBA8888);
  return QCryptographicHash::hash(QByteArrayView(reinterpret_cast<const char*>(rgba.constBits()), rgba.sizeInBytes()), QCryptographicHash::Sha256).toHex();
}
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  if (argc == 2 && QByteArray(argv[1]) == "mapping") {
    std::atomic_bool cancel{false};
    for (auto format : {QImage::Format_RGB32, QImage::Format_ARGB32, QImage::Format_ARGB32_Premultiplied,
                        QImage::Format_RGBX8888, QImage::Format_RGBA8888, QImage::Format_RGBA8888_Premultiplied}) {
      // Two active pixels per row; deliberately unequal padding must be ignored.
      alignas(4) unsigned char bytes[32] = {};
      QImage image(bytes, 2, 2, 16, format);
      image.fill(QColor(31,83,149));
      bytes[8] = 17; bytes[24] = 99;
      require(!adaptiveNonuniform(image,cancel));
      bytes[16] ^= 1;
      require(adaptiveNonuniform(image,cancel));
      cancel.store(true); require(!adaptiveNonuniform(image,cancel)); cancel.store(false);
    }
    QImage unsupported(3,3,QImage::Format_Grayscale8); unsupported.fill(1); unsupported.setPixelColor(2,2,Qt::white);
    require(!adaptiveNonuniform(unsupported,cancel));
    QImage alpha(2,1,QImage::Format_RGBA8888); alpha.fill(QColor(1,2,3,4)); alpha.setPixelColor(1,0,QColor(1,2,3,5));
    require(adaptiveNonuniform(alpha,cancel));
    require(!adaptiveNonuniform(QImage(),cancel));
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
  struct Input { QString name; int tier; QImage image; };
  QList<Input> inputs;
  for (const QString name : {QString("textured"), QString("flat"), QString("alpha"), QString("oriented"), QString("two-color"), QString("gradient"), QString("panel")}) {
    for (int tier : {128, 256, 512, 1024}) {
      QImage image;
      if (name != "textured" && name != "oriented") {
        QImage source(3200, 2400, QImage::Format_RGBA8888);
        source.setColorSpace(QColorSpace::SRgb);
        source.fill(QColor(31, 83, 149, 255));
        if (name == "alpha") {
          for (int y = 0; y < source.height(); ++y)
            for (int x = 0; x < source.width(); ++x)
              source.setPixelColor(x, y, QColor((x * 13 + y * 3) % 256, (x + y * 7) % 256, (x * 5 + y) % 256, (x + y * 3) % 256));
        }
        if (name == "two-color" || name == "gradient" || name == "panel") {
          for (int y = 0; y < 2400; ++y)
            for (int x = 0; x < 3200; ++x) {
              QColor color;
              if (name == "two-color") color = x < 1600 ? QColor(255,255,255) : QColor(31,83,149);
              if (name == "gradient") { int v = 255*x/3199; color = QColor(v,v,v); }
              if (name == "panel") color = x >= 400 && x < 2800 && y >= 300 && y < 2100 ? QColor(31,83,149) : QColor(240,240,240);
              source.setPixelColor(x,y,color);
            }
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
      corpus.append(QJsonObject{{"id",id},{"tier",tier},{"width",image.width()},{"height",image.height()},{"pixels",QString(pixels(image))},{"alpha",image.hasAlphaChannel()},{"icc",QString(QCryptographicHash::hash(image.colorSpace().iccProfile(), QCryptographicHash::Sha256).toHex())}});
      inputs.append({name,tier,image});
      QFile frozen(directory + '/' + id + "-input.rgba");
      require(frozen.open(QIODevice::WriteOnly | QIODevice::NewOnly));
      auto rgba = image.convertToFormat(QImage::Format_RGBA8888);
      require(frozen.write(reinterpret_cast<const char*>(rgba.constBits()), rgba.sizeInBytes()) == rgba.sizeInBytes());
    }
  }
  QFile manifest(directory + "/inputs.json");
  require(manifest.open(QIODevice::WriteOnly | QIODevice::NewOnly));
  require(manifest.write(QJsonDocument(corpus).toJson()) > 0); manifest.close();
  for (const auto& input : inputs) {
      const auto& name = input.name; const auto tier = input.tier; const auto& image = input.image;
      const QString id = name + '-' + QString::number(tier);
      // Exactly identical source metadata and cache key for all modes and observations.
      Store_default::Request request{QUrl::fromLocalFile(directory + "/source-" + name), QDateTime::fromMSecsSinceEpoch(1700000000123LL), 1234567, image.size(), Store_default::Kind::Raster, "encoding-trial-v1", tier};
      Store_adaptive::Request requestAdaptive{request.uri, request.modified, request.size, request.required, Store_adaptive::Kind::Raster, request.revision, tier};
      const auto path = Store_default::cachePath(request.uri, tier);

      auto store = [&](int mode, bool warmup, int block, int observation) {
        QElapsedTimer timer; timer.start();
        bool okay = mode == 0 ? Store_default::store(request,image,cancelled,{}) : Store_adaptive::store(requestAdaptive,image,cancelled,{});
        auto ns = timer.nsecsElapsed();
        require(okay);
        QFile file(path); require(file.open(QIODevice::ReadOnly));
        const auto bytes = file.readAll();
        QImage decoded; require(decoded.loadFromData(bytes,"PNG"));
        QJsonObject texts;
        for (auto key : decoded.textKeys()) texts[key] = decoded.text(key);
        require(pixels(image) == pixels(decoded) && image.hasAlphaChannel() == decoded.hasAlphaChannel() && image.colorSpace() == decoded.colorSpace());
        rows.append(QJsonObject{{"id",id},{"mode",mode == 0 ? "default" : "adaptive"},{"warmup",warmup},{"block",block},{"observation",observation},{"ns",ns},{"bytes",bytes.size()},{"sha256",QString(QCryptographicHash::hash(bytes,QCryptographicHash::Sha256).toHex())},{"pixels",QString(pixels(decoded))},{"alpha",decoded.hasAlphaChannel()},{"icc",QString(QCryptographicHash::hash(decoded.colorSpace().iccProfile(),QCryptographicHash::Sha256).toHex())},{"metadata",texts}});
        // Retain each mode's exact bytes for independent decoding, outside timing.
        QFile retained(directory + '/' + id + '-' + (mode == 0 ? "default" : "adaptive") + ".png");
        require(retained.open(QIODevice::WriteOnly)); require(retained.write(bytes) == bytes.size());
      };
      for (int mode=0; mode<2; ++mode) store(mode,true,-1,0);
      for (int block=0; block<6; ++block)
        for (int offset=0; offset<2; ++offset)
          for (int observation=0; observation<5; ++observation) store((block+offset)%2,false,block,observation);
  }
  QFile output(QString::fromLocal8Bit(argv[2])); require(output.open(QIODevice::WriteOnly | QIODevice::NewOnly));
  require(output.write(QJsonDocument(QJsonObject{{"qt",qVersion()},{"corpus",corpus},{"rows",rows}}).toJson()) > 0);
  return 0;
}
