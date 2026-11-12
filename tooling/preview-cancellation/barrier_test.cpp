#include "diagnostic.h"
#include <QCoreApplication>
#include <QThread>
#include <future>
#include <thread>
#include <optional>
namespace D = CancellationDiagnostic;
int main(int argc, char** argv) {
  QCoreApplication app(argc,argv);
  const std::string mode=argc>1?argv[1]:"release";
  if(mode=="result-status") {
    enum class Runtime { Success, Cancelled, Failure };
    enum class Outcome { Success, Cancelled, Failure };
    enum class Error { None, Failure };
    struct Result {
      Runtime runtime=Runtime::Success;
      std::optional<Outcome> raster_outcome=Outcome::Success;
      struct { Error kind=Error::None; } error;
      bool pixels=false;
    } result;
    if(!D::successfulResult(result)) return 10; // metadata-only final
    result.pixels=true;
    if(!D::successfulResult(result)) return 11;
    result.runtime=Runtime::Cancelled;
    if(D::successfulResult(result)) return 12;
    result.runtime=Runtime::Failure;
    if(D::successfulResult(result)) return 13;
    result.runtime=Runtime::Success;
    result.raster_outcome=Outcome::Cancelled;
    if(D::successfulResult(result)) return 14;
    result.raster_outcome=Outcome::Failure;
    if(D::successfulResult(result)) return 15;
    result.raster_outcome.reset();
    if(D::successfulResult(result)) return 16;
    result.raster_outcome=Outcome::Success;
    result.error.kind=Error::Failure;
    return D::successfulResult(result)?17:0;
  }
  auto worker=std::async(std::launch::async,[]{return D::gate("active");});
  const auto limit=std::chrono::steady_clock::now()+std::chrono::seconds(1);
  while(!D::seen("active_reached") && std::chrono::steady_clock::now()<limit) {
    QCoreApplication::processEvents(); QThread::yieldCurrentThread();
  }
  if(!D::seen("active_reached")) { D::releaseAll(); return 1; }
  if(mode=="release") {
    D::release("active");
    return worker.get() && !D::failed && D::seen("active_resumed")?0:2;
  }
  if(mode=="watchdog") {
    const bool ok=worker.get();
    // A watchdog failure releases other blocked gates immediately.
    auto other=std::async(std::launch::async,[]{return D::gate("other");});
    return !ok && D::failed && D::seen("barrier_timeout") && other.get()?0:3;
  }
  bool observed=false;
  std::thread supervisor([&]{
    std::unique_lock lock(D::mutex);
    observed=D::changed.wait_for(lock,std::chrono::milliseconds(mode=="supervisor"?1000:20),[]{
      for(const auto& row:D::records) if(row["event"]=="destructor_cancel") return true;
      return false;
    });
    lock.unlock();
    if(observed) D::release("active"); else D::releaseAll();
  });
  // Stand-in destructor, on the owning thread; supervisor only observes and releases.
  if(mode=="supervisor") D::probe("destructor_cancel",0,{{"cancelled",true}});
  const bool released=worker.get(); supervisor.join();
  return released && !D::failed && observed==(mode=="supervisor")?0:4;
}
