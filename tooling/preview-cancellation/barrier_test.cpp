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
  const StandbyTrace::Context captured{41,42,43,44,45,"service_control"};
  StandbyTrace::current=captured;
  const auto owner_tid=qint64(syscall(SYS_gettid));
  bool observed=false, restored=false;
  std::thread supervisor([&]{
    const StandbyTrace::Context prior{91,92,93,94,95,"prior"};
    StandbyTrace::current=prior;
    auto context=captured;
    if(mode=="supervisor-missing") context.service=0;
    observed=D::superviseDestruction(context,std::chrono::milliseconds(100));
    const auto after=StandbyTrace::current;
    restored=after.service==prior.service && after.observation==prior.observation &&
        after.job==prior.job && after.worker==prior.worker && after.preparation==prior.preparation &&
        std::string(after.role)==prior.role;
  });
  // Stand-in destructor stays on the owning thread.
  if(mode=="supervisor") D::probe("destructor_cancel",0,{{"cancelled",true}});
  if(mode=="supervisor-foreign" || mode=="supervisor-observation" || mode=="supervisor-uncancelled") {
    auto foreign=captured;
    if(mode=="supervisor-foreign") ++foreign.service;
    if(mode=="supervisor-observation") ++foreign.observation;
    StandbyTrace::Bind bind(foreign);
    D::probe("destructor_cancel",0,{{"cancelled",mode!="supervisor-uncancelled"}});
  }
  const bool released=worker.get(); supervisor.join();
  if(!released || !restored || observed!=(mode=="supervisor") || D::failed==observed) return 4;
  if(!observed) {
    auto other=std::async(std::launch::async,[]{return D::gate("other");});
    return D::released_all && !D::seen("active_release") && other.get()?0:5;
  }
  QJsonObject cancellation, release, resumed;
  for(const auto& row:D::records) {
    if(row["event"]=="destructor_cancel") cancellation=row;
    if(row["event"]=="active_release") release=row;
    if(row["event"]=="active_resumed") resumed=row;
  }
  return release["service"].toInteger()==41 && release["observation"].toInteger()==42 &&
      release["job"].toInteger()==43 && release["worker"].toInteger()==44 &&
      release["preparation"].toInteger()==45 && release["role"]=="service_control" &&
      release["tid"].toInteger()!=owner_tid &&
      cancellation["order"].toInteger()<release["order"].toInteger() &&
      release["order"].toInteger()<resumed["order"].toInteger()?0:6;
}
