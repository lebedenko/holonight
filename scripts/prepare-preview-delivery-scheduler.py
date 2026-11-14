#!/usr/bin/env python3
"""Freeze private public-dispatch probes without building or launching processes."""
import argparse
import difflib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('scheduler_overhead', ROOT/'scripts/measure-preview-delivery-overhead.py')
o = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o)
require, write = o.require, o.write
WARNING = 'uncompiled, unexecuted, incremental overhead unmeasured'
HEADER = r'''
// Separate supplemental stream; dispatch context is never copied into worker context.
#include <QCoreApplication>
#include <QEvent>
namespace SchedulerTrace {
inline std::atomic<unsigned long long> sequence{1};
inline thread_local unsigned long long dispatch=0;
inline void event(const char* edge, unsigned long long id, unsigned long long parent,
                  long long captured, unsigned long long publication=0) {
  char line[768];
  int n=std::snprintf(line,sizeof(line),"SCHEDULER {\"version\":1,\"ns\":%lld,\"pid\":%d,\"tid\":%ld,\"dispatch\":%llu,\"parent\":%llu,\"publication\":%llu,\"edge\":\"%s\"}\n",
    captured,getpid(),syscall(SYS_gettid),id,parent,publication,edge);
  if(n>0 && n<static_cast<int>(sizeof(line))) { auto ignored=write(2,line,n); (void)ignored; }
}
struct Dispatch {
  unsigned long long parent=dispatch, id=sequence.fetch_add(1);
  Dispatch() { const auto t=DeliveryTrace::now(); dispatch=id; event("enter",id,parent,t); }
  ~Dispatch() { const auto t=DeliveryTrace::now(); dispatch=parent; event("exit",id,parent,t); }
};
inline void publication() {
  const auto t=DeliveryTrace::now();
  event("publication",dispatch,0,t,StandbyTrace::current.delivery_publication);
}
class Application : public QCoreApplication {
public:
  using QCoreApplication::QCoreApplication;
  bool notify(QObject* receiver, QEvent* event) override {
    if(event->type()!=QEvent::MetaCall) return QCoreApplication::notify(receiver,event);
    Dispatch scope;
    return QCoreApplication::notify(receiver,event);
  }
};
}
'''


def feasibility():
    paths = ['/proc/version', '/proc/sys/kernel/perf_event_paranoid',
             '/proc/sys/kernel/kptr_restrict', '/sys/kernel/tracing/trace_clock',
             '/usr/lib/cmake/Qt6Core/Qt6CoreConfigVersion.cmake',
             '/sys/kernel/tracing/events/sched/sched_switch/format',
             '/sys/kernel/tracing/events/sched/sched_wakeup/format']
    evidence = {}
    for name in paths:
        try:
            evidence[name] = dict(status='read', text=Path(name).read_text())
        except OSError as error:
            evidence[name] = dict(status='unverified prerequisite', reason=str(error))
    identities = {}
    for pattern in ('/var/lib/pacman/local/perf-*/desc', '/var/lib/pacman/local/qt6-base-*/desc', '/usr/bin/perf', '/usr/lib/libQt6Core.so*', '/usr/lib/modules/*/build/include/generated/utsrelease.h'):
        import glob
        for name in glob.glob(pattern):
            path = Path(name)
            if path.is_file():
                identities[name] = dict(resolved=str(path.resolve()), sha256=o.digest(path))
    return dict(kernel=os.uname()._asdict() if hasattr(os.uname(), '_asdict') else list(os.uname()),
                identities=identities, evidence=evidence, capture_ready=False,
                limitations='Read-only files only; clock compatibility, initial task state, permissions and loss-free capture require a later authorized pilot.')


def verify_generated(output, prepared):
    """Independent byte replay, citations and complete allowed-file inventory."""
    anchors=o.read(output/'anchors.json')
    require(len({a['file'] for a in anchors})==len(anchors),'duplicate replay path')
    by_name={a['file']:a for a in anchors}
    expected_patches=set()
    for i,anchor in enumerate(anchors,1):
        relative=Path(anchor['file'])
        require(len(relative.parts)>=3 and relative.parts[0] in 'ABCD' and relative.parts[1] in o.prep.GROUPS and '..' not in relative.parts,'invalid anchor path')
        patch=relative.parts[0]+'-'+str(i)+'.diff'; expected_patches.add(patch)
        original=prepared/'v4'/relative
        expected=''.join(difflib.unified_diff(anchor['before'].splitlines(True),anchor['after'].splitlines(True),fromfile=str(original),tofile=str(output/relative)))
        require((output/patch).read_text()==expected,'patch excerpt mismatch')
    require({path.name for path in output.glob('*.diff')}==expected_patches,'patch inventory mismatch')
    for variant in 'ABCD':
        source=prepared/'v4'/variant
        require((output/variant/'trace.h').read_bytes()==(source/'trace.h').read_bytes()+HEADER.encode(), 'header replay mismatch')
        for group in o.prep.GROUPS:
            original=o.inventory(source/group); generated=o.inventory(output/variant/group)
            require(set(original)==set(generated),'source file set mismatch')
            for name in original:
                key=variant+'/'+group+'/'+name
                old=(source/group/name).read_bytes()
                # Derive permitted edits from frozen input, never from recorded anchors.
                expected=old.replace(str(source/'trace.h').encode(),str(output/variant/'trace.h').encode())
                if Path(name).suffix=='.cpp':
                    expected=expected.replace(b'QCoreApplication app(argc, argv);',b'SchedulerTrace::Application app(argc, argv);')
                    probe=b'DeliveryTrace::Scope delivery_callback("callback_execution");'
                    require(expected.count(probe)<=1,'duplicate callback anchor')
                    expected=expected.replace(probe,b'SchedulerTrace::publication();\n          '+probe)
                include=b'#include "'+str(output/variant/'trace.h').encode()+b'"'
                if b'SchedulerTrace::Application app' in expected and include not in expected:
                    expected=include+b'\n'+expected
                if old!=expected:
                    require(key in by_name,'missing substitution anchor')
                    require(by_name[key]['before'].encode()==old and by_name[key]['after'].encode()==expected,'unauthorized preparation edit')
                else:
                    require(key not in by_name,'unexpected preparation anchor')
                require((output/key).read_bytes()==expected,'replay mismatch: '+key)
    expected_citations=[]
    for variant in 'ABCD':
        target=output/variant
        require(sum(b'SchedulerTrace::Application app(argc, argv);' in (target/g/n).read_bytes() for g in o.prep.GROUPS for n in o.inventory(target/g))>=1,'missing application substitution')
        for path in [target/'trace.h',*(target/'source').rglob('*.cpp'),*(target/'harness-source').rglob('*.cpp')]:
            lines=path.read_text().splitlines()
            for i,line in enumerate(lines):
                if 'SchedulerTrace::' in line or 'event("' in line and path.name=='trace.h':
                    expected_citations.append(dict(file=str(path),sha256=o.digest(path),line=i+1,text=line,excerpt='\n'.join(lines[max(0,i-3):i+4])))
    require(o.read(output/'source-citations.json')==expected_citations,'missing or altered probe excerpts')
    require(set(by_name)=={str(path.relative_to(output)) for v in 'ABCD' for g in o.prep.GROUPS for path in (output/v/g).rglob('*') if path.is_file() and path.read_bytes()!=(prepared/'v4'/v/g/path.relative_to(output/v/g)).read_bytes()},'anchor inventory mismatch')
    for citation in o.read(output/'source-citations.json'):
        path=Path(citation['file'])
        require(path.resolve().is_relative_to(output.resolve()) and not path.is_symlink(),'citation escape')
        lines=path.read_text().splitlines(); i=citation['line']-1
        require(o.digest(path)==citation['sha256'] and lines[i]==citation['text'] and '\n'.join(lines[max(0,i-3):i+4])==citation['excerpt'],'probe mismatch')
    return dict(passed=True)


def prepare(prepared, gap, output):
    o.fresh(output, prepared, gap)
    before = {}; result = dict(status='blocked', warning=WARNING)
    tool_paths=[Path(__file__).resolve(),ROOT/'scripts/analyze-preview-delivery-scheduler.py',ROOT/'tests/test_preview_delivery_scheduler.py',ROOT/'scripts/run-preview-delivery-scheduler.py',ROOT/'scripts/normalize-preview-delivery-perf.py',ROOT/'tests/test_preview_delivery_scheduler_pilot.py']
    tools={str(path):o.digest(path) for path in tool_paths}
    try:
        require(all(p.absolute()==p.resolve() for p in (prepared,gap)), 'symlink input ancestors refused')
        before = {str(p):o.inventory(p) for p in (prepared,gap)}
        o.verify(prepared); o.check_output(gap)
        assessment=o.read(gap/'assessment.json'); integrity=o.read(gap/'integrity.json')
        require(assessment['status']=='complete' and all(c['passed'] for c in integrity['final_checks'].values()), 'gap integrity blocked')
        independent=o.read(gap/'independent-verification.json')
        require(independent['status']=='passed' and all(c['passed'] for c in independent['checks'].values()), 'independent gap verification blocked')
        require(integrity['before'][str(prepared)]==before[str(prepared)], 'gap preparation identity mismatch')
        anchors=[]; citations=[]
        for variant in 'ABCD':
            source=prepared/'v4'/variant; target=output/variant
            target.mkdir()
            (target/'trace.h').write_bytes((source/'trace.h').read_bytes()+HEADER.encode())
            for group in o.prep.GROUPS:
                shutil.copytree(source/group,target/group)
                for path in sorted((target/group).rglob('*')):
                    if not path.is_file(): continue
                    old=path.read_bytes(); new=old.replace(str(source/'trace.h').encode(),str(target/'trace.h').encode())
                    if path.suffix=='.cpp':
                        new=new.replace(b'QCoreApplication app(argc, argv);',b'SchedulerTrace::Application app(argc, argv);')
                        anchor=b'DeliveryTrace::Scope delivery_callback("callback_execution");'
                        if anchor in new:
                            require(new.count(anchor)==1,'duplicate callback anchor')
                            new=new.replace(anchor,b'SchedulerTrace::publication();\n          '+anchor)
                    if b'SchedulerTrace::Application app' in new and b'#include "'+str(target/'trace.h').encode()+b'"' not in new:
                        new=b'#include "'+str(target/'trace.h').encode()+b'"\n'+new
                    path.write_bytes(new)
                    if old!=new:
                        relative=str(path.relative_to(output))
                        anchors.append(dict(file=relative, before=old.decode(), after=new.decode()))
                        (output/(variant+'-'+str(len(anchors))+'.diff')).write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile=str(source/group/path.relative_to(target/group)),tofile=str(path))))
            require(sum('SchedulerTrace::publication();' in a['after'] for a in anchors if a['file'].startswith(variant+'/'))==1,'missing publication anchor')
            for path in [target/'trace.h',*(target/'source').rglob('*.cpp'),*(target/'harness-source').rglob('*.cpp')]:
                lines=path.read_text().splitlines()
                for i,line in enumerate(lines):
                    if 'SchedulerTrace::' in line or 'event("' in line and path.name=='trace.h':
                        citations.append(dict(file=str(path),sha256=o.digest(path),line=i+1,text=line,excerpt='\n'.join(lines[max(0,i-3):i+4])))
        write(output/'anchors.json',anchors); write(output/'source-citations.json',citations)
        write(output/'independent-source-verification.json',verify_generated(output,prepared))
        write(output/'host-feasibility.json',feasibility())
        write(output/'offline-tools.json',tools)
        result.update(status='prepared', variants=list('ABCD'), capture_ready=False)
    except (OSError,ValueError,KeyError,TypeError) as error:
        result['failure']=str(error)
    finally:
        checks={}
        for p in (prepared,gap):
            try:
                require(o.inventory(p)==before.get(str(p)), 'input drift')
                o.check_output(p); checks[str(p)]=dict(passed=True)
            except (OSError,ValueError,KeyError,TypeError) as error:
                checks[str(p)]=dict(passed=False,failure=str(error))
        checks['tools']=dict(passed=all(o.digest(Path(name))==sha for name,sha in tools.items()))
        if not all(c['passed'] for c in checks.values()): result['status']='blocked'
        write(output/'integrity.json',dict(before=before,tools=tools,final_checks=checks))
        write(output/'assessment.json',result)
        (output/'ASSESSMENT.md').write_text('Status: '+result['status']+'\n\n**'+WARNING+'**.\nPublic MetaCall dispatch boundaries only. Exact queue insertion unavailable. Preparation does not establish capture readiness. C qualification, D pilot, unavailable cleanup and unevaluated conditions remain unchanged.\n')
        o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('prepared','gap-analysis','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    result=prepare(args.prepared,args.gap_analysis,args.output)
    print(json.dumps(result)); sys.exit(result['status']!='prepared')
