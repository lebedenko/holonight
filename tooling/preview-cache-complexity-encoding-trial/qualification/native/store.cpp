#include <holonight_thumbnails/cache.h>
#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTemporaryDir>
#include <thread>

static void require(bool value) { if (!value) std::abort(); }
int main(int argc,char** argv) {
  QCoreApplication app(argc,argv);
  require(argc==4);
  const QString shared=QString::fromLocal8Bit(argv[1]), arm=QString::fromLocal8Bit(argv[2]);
  require(QDir().mkpath(shared));
  QTemporaryDir cache;
  require(cache.isValid());
  qputenv("XDG_CACHE_HOME",QFile::encodeName(cache.path()));
  QImage image(128,128,QImage::Format_RGBA8888);
  for (int y=0;y<128;++y) for (int x=0;x<128;++x)
    image.setPixelColor(x,y,QColor((x*13+y*7)%256,(x*3+y*17)%256,(x+y)%256));
  std::atomic_bool cancelled{false};
  HolonightThumbnails::Request request{QUrl::fromLocalFile(shared+"/source"),
    QDateTime::fromMSecsSinceEpoch(1700000000123LL),1234567,{128,128},HolonightThumbnails::Kind::Svg,"encoding-trial-v1",128};
  require(HolonightThumbnails::store(request,image,cancelled));
  auto path=HolonightThumbnails::cachePath(request.uri,128);
  QFile encoded(path); require(encoded.open(QIODevice::ReadOnly));
  QFile svg(shared+'/'+arm+"-svg.png"); require(svg.open(QIODevice::WriteOnly|QIODevice::NewOnly));
  require(svg.write(encoded.readAll())>0); svg.close(); encoded.close();
  request.kind=HolonightThumbnails::Kind::Raster;
  require(HolonightThumbnails::store(request,image,cancelled));
  require(HolonightThumbnails::lookup(request,cancelled).has_value());
  QImage cross(shared+"/control-raster.png");
  if (arm=="candidate") require(!cross.isNull() && cross.convertToFormat(QImage::Format_RGBA8888)==image);
  require(encoded.open(QIODevice::ReadOnly));
  QFile raster(shared+'/'+arm+"-raster.png"); require(raster.open(QIODevice::WriteOnly|QIODevice::NewOnly));
  require(raster.write(encoded.readAll())>0); raster.close(); encoded.close();
  cancelled.store(true); require(!HolonightThumbnails::store(request,image,cancelled)); cancelled.store(false);
  // Concurrent commits must publish one complete image and preserve valid metadata.
  QImage other=image; other.fill(Qt::blue);
  bool a=false,b=false;
  std::thread first([&] { a=HolonightThumbnails::store(request,image,cancelled); });
  std::thread second([&] { b=HolonightThumbnails::store(request,other,cancelled); });
  first.join(); second.join(); require(a && b);
  auto result=HolonightThumbnails::lookup(request,cancelled); require(result.has_value());
  auto pixels=result->convertToFormat(QImage::Format_RGBA8888);
  require(pixels==image || pixels==other);
  QFile blocked(cache.filePath("blocked")); require(blocked.open(QIODevice::WriteOnly)); blocked.close();
  qputenv("XDG_CACHE_HOME",QFile::encodeName(blocked.fileName()));
  require(!HolonightThumbnails::store(request,image,cancelled));
  QFile output(QString::fromLocal8Bit(argv[3])); require(output.open(QIODevice::WriteOnly|QIODevice::NewOnly));
  require(output.write(QJsonDocument(QJsonObject{{"svg_fallback",true},{"cross_arm_readability",true},
    {"write_failure",true},{"concurrent_atomic",true},{"cancelled_store",true}}).toJson())>0);
}
