#include "diagnostic.h"
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QFile>
#include <QTemporaryDir>
#include <QThread>
#include <HolonightFileBrowser/preview/preview_service.h>
#include <HolonightFileBrowser/preview/image_policy.h>
#include <sys/stat.h>
#include <thread>

struct PreviewServiceTestAccess {
  static void beforeDecode(PreviewService& s, std::function<void()> f) { s.before_full_decode_for_test_=std::move(f); }
  static auto cancel(const PreviewService& s) { return s.cancellation_; }
  static auto exif(const PreviewService& s) { return s.exif_; }
  static bool timedOut(const PreviewService& s) { return s.timed_out_; }
};
namespace D = CancellationDiagnostic;
namespace {
bool waitFor(const std::function<bool()>& condition, int milliseconds=1000) {
  QElapsedTimer timer; timer.start();
  while (!condition() && timer.elapsed()<milliseconds) {
    QCoreApplication::processEvents(); QThread::yieldCurrentThread();
  }
  return condition();
}
void require(bool value, const char* message) { if (!value) throw std::runtime_error(message); }
void target(PreviewService& s, const QString& path) { s.setTarget(path,false,0,{},S_IFREG|0600,false,{}); }
std::atomic_bool cleanup_failure{false};
void messages(QtMsgType, const QMessageLogContext&, const QString& text) {
  if (text.startsWith("Preview runtime failure 4")) cleanup_failure=true;
  fprintf(stderr,"%s\n",qPrintable(text));
}
}
int main(int argc,char** argv) {
  QCoreApplication app(argc,argv);
  if (argc!=7) return 2;
  qInstallMessageHandler(messages);
  D::scenario=argv[4];
  D::ledger.open(std::string(argv[5])+".ledger.jsonl");
  D::barriers.open(std::string(argv[5])+".barriers.jsonl");
  if (!D::ledger || !D::barriers) return 3;
  QJsonObject result{{"scenario",argv[4]}, {"success",false}, {"services",1}};
  QTemporaryDir temporary(QString::fromLocal8Bit(argv[5])+".work-XXXXXX");
  temporary.setAutoRemove(false);
  std::unique_ptr<PreviewService> service;
  std::thread supervisor;
  bool supervisor_ok=false;
  try {
    require(temporary.isValid(),"temporary directory");
    qputenv("XDG_CACHE_HOME",QFile::encodeName(temporary.filePath("cache")));
    auto primary=temporary.filePath("primary.png"), replacement=temporary.filePath("replacement.jpg");
    require(QFile::copy(argv[2],primary) && QFile::copy(argv[3],replacement),"fixture copies");
    // Independent in-process reference: no session, runtime helper, or service cache.
    QFile reference(replacement); require(reference.open(QIODevice::ReadOnly),"reference open");
    const std::atomic_bool no_cancel{false};
    const auto inspection=HolonightImages::inspect(reference,kPreviewImageLimits,no_cancel);
    const auto expected=HolonightImages::decode(reference,{.limits=kPreviewImageLimits,.bound={256,256}},no_cancel);
    require(expected.outcome==HolonightImages::Outcome::Success,"reference decode");
    StandbyTrace::current.service=StandbyTrace::identity();
    StandbyTrace::current.observation=1; StandbyTrace::current.role="service_control";
    service=std::make_unique<PreviewService>(HolonightFileBrowser::ImageRuntimeOptions{QString::fromLocal8Bit(argv[1])});
    service->setRequestedSize(PreviewService::PreviewConsumer::Pane,{256,256});
    PreviewServiceTestAccess::beforeDecode(*service,[]{
      if (StandbyTrace::current.job==D::primary && D::scenario!="preparation") D::gate("active");
    });
    target(*service,primary);
    const auto cancelled=PreviewServiceTestAccess::cancel(*service);
    require(bool(cancelled),"primary cancellation token");
    if (D::scenario=="preparation") {
      require(waitFor([]{return D::seen("preparation_reached") && D::seen("pending");}),"preparation/pending acknowledgement");
      service->clear(); D::probe("cancel",0,{{"cancelled",cancelled->load()}});
      service->refreshRuntime();
      require(waitFor([]{return D::seen("preparation_cancel_set");}),"preparation cancellation acknowledgement");
      D::release("preparation");
      require(waitFor([]{return D::seen("preparation_cancel_observed") && D::seen("retirement_complete") && D::seen("preparation_terminal");},10000),"preparation drain");
    } else {
      require(waitFor([]{return D::seen("active_reached");},10000),"active acknowledgement");
      if (D::scenario=="destruction") {
        target(*service,replacement);
        require(cancelled->load(),"superseded primary cancellation");
        require(waitFor([]{std::lock_guard lock(D::mutex); for(const auto& r:D::records) if(r["event"]=="pending" && r["job"].toInteger()!=qint64(D::primary)) return true; return false;}),"second request pending");
        supervisor=std::thread([&]{
          std::unique_lock lock(D::mutex);
          supervisor_ok=D::changed.wait_for(lock,std::chrono::seconds(1),[]{
            for(const auto& r:D::records) if(r["event"]=="destructor_cancel" && r["cancelled"].toBool()) return true;
            return false;
          });
          lock.unlock();
          if(supervisor_ok) D::release("active"); else D::releaseAll();
        });
        service.reset(); supervisor.join();
        require(supervisor_ok,"destructor supervisor acknowledgement");
      } else {
        service->clear(); D::probe("cancel",0,{{"cancelled",cancelled->load()}});
        require(cancelled->load(),"active cancellation acknowledgement");
        D::release("active");
        if (D::scenario=="cleanup") {
          require(waitFor([]{return D::seen("retirement_reached");}),"retirement acknowledgement");
          target(*service,replacement);
          require(waitFor([]{std::lock_guard lock(D::mutex); for(const auto& r:D::records) if(r["event"]=="pending" && r["job"].toInteger()!=qint64(D::primary)) return true; return false;}),"replacement pending during retirement");
          D::release("retirement");
        } else require(waitFor([]{return D::seen("terminal",D::primary);},10000),"active terminal completion");
      }
    }
    if (D::scenario!="destruction") {
      if(D::scenario!="cleanup") target(*service,replacement);
      require(waitFor([&]{return !service->busy();},10000),"replacement completion");
      require(!PreviewServiceTestAccess::timedOut(*service),"service timeout");
      const bool pixels=service->hasImage() && service->image()==expected.image;
      const bool metadata=service->sourcePixelSize()==inspection.orientedSize && PreviewServiceTestAccess::exif(*service)==ExifReader::format(inspection.metadata);
      result.insert("correct_pixels",pixels); result.insert("correct_metadata",metadata);
      require(pixels && metadata,"replacement content");
      service.reset();
    }
    QCoreApplication::processEvents();
    require(!D::failed && !cleanup_failure.load(),"barrier or native cleanup failure");
    result.insert("success",true);
  } catch (const std::exception& error) {
    result.insert("failure",error.what()); D::releaseAll();
    if(supervisor.joinable()) supervisor.join();
    service.reset();
  }
  result.insert("barrier_timeout",D::failed);
  result.insert("cleanup_failure",cleanup_failure.load());
  QFile output(argv[6]);
  if(!output.open(QIODevice::WriteOnly|QIODevice::NewOnly)) return 4;
  output.write(QJsonDocument(result).toJson());
  return result["success"].toBool()?0:1;
}
