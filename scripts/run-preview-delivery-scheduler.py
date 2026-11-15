#!/usr/bin/env python3
"""Bounded B/160x80 scheduler pilot. Preflight precedes all builds and workloads."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import pwd
import re
import select
import signal
import subprocess
import sys
import time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

p=module('pilot_preparation','prepare-preview-delivery-scheduler.py')
a=module('pilot_analysis','analyze-preview-delivery-scheduler.py')
n=module('pilot_normalizer','normalize-preview-delivery-perf.py')
o=p.o
require,read,write=o.require,o.read,o.write
HISTORICAL=ROOT/'build/preview-delivery-scheduler-20261114-05'
PREPARED=ROOT/'build/preview-delivery-overhead-20261114-03'
GAP=ROOT/'build/preview-delivery-overhead-gaps-20261114-01'
INSTALLER=ROOT/'build/preview-delivery-runtime-smoke-20261113-02'
EVENTS=('sched_switch','sched_wakeup','sched_wakeup_new','sched_process_fork','sched_process_exec','sched_process_exit')
BOUNDS=dict(variant='B',fixture='160x80.png',observations=[1,10],invocations=2,timeout_seconds=30,termination_grace_seconds=5,retries=0,mmap_pages_per_cpu=256,all_cpus=True,clock='CLOCK_MONOTONIC',stack_sampling=False)
ERRORS=(OSError,ValueError,KeyError,TypeError,IndexError,RuntimeError,subprocess.SubprocessError)


def tools():
    paths=[Path(__file__).resolve(),ROOT/'scripts/prepare-preview-delivery-scheduler.py',ROOT/'scripts/analyze-preview-delivery-scheduler.py',ROOT/'scripts/normalize-preview-delivery-perf.py']
    return {str(path):o.digest(path) for path in paths}


def session():
    account=pwd.getpwuid(1000)
    env={k:os.environ[k] for k in ('PATH','LANG','LC_ALL','TZ') if k in os.environ}
    env.update(HOME=account.pw_dir,USER=account.pw_name,LOGNAME=account.pw_name,XDG_RUNTIME_DIR='/run/user/1000',DBUS_SESSION_BUS_ADDRESS='unix:path=/run/user/1000/bus',QT_QPA_PLATFORM='offscreen')
    credentials=dict(user=1000,group=account.pw_gid,extra_groups=os.getgrouplist(account.pw_name,account.pw_gid)) if os.geteuid()==0 else {}
    require(os.geteuid() in (0,1000),'UID 1000 or privileged wrapper required')
    return env,credentials


def residuals(output):
    # Independent of scope accounting, retain process identities and matching cmdlines.
    found=[]
    for path in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            text=path.read_bytes().replace(b'\0',b' ').decode(errors='replace')
            if ('preview-benchmark' in text or 'holonight-images-helper' in text or ('perf' in text and '--control' in text)) and int(path.parent.name)!=os.getpid():
                # Interpreter shell/runner arguments are not a residual preview process.
                executable=path.read_bytes().split(b'\0',1)[0].decode(errors='replace')
                if Path(executable).name in ('preview-benchmark','holonight-images-helper','perf'): found.append(dict(pid=int(path.parent.name),cmdline=text))
        except (FileNotFoundError,ProcessLookupError,PermissionError): continue
    write(output/'residual-processes.json',found)
    require(not found,'residual preview or recorder processes')


def sealed_action(output, inputs, action):
    o.fresh(output,*inputs); before={}; result=dict(status='blocked',bounds=BOUNDS)
    identities=tools()
    try:
        require(all(x.absolute()==x.resolve() for x in inputs),'symlink input ancestors refused')
        before={str(x):o.inventory(x) for x in inputs}
        action(result)
    except ERRORS as error:
        if 'failure' in result: result['action_failure']=str(error)
        else: result['failure']=str(error)
    finally:
        checks={}
        actions=[(str(x),lambda x=x:require(o.inventory(x)==before.get(str(x)),'input drift')) for x in inputs]
        def scopes():
            env,credentials=session(); value=o.gate.scope_snapshot(1000,env,credentials)
            write(output/'scopes-final.json',value); require(value['isolated'],'final scope isolation unverified')
        actions += [('scopes',scopes),('tools',lambda:o.gate.smoke.verify_hashes(Path('/'),identities)),('residual_processes',lambda:residuals(output))]
        for name,check in actions:
            try: check(); checks[name]=dict(passed=True)
            except ERRORS as error: checks[name]=dict(passed=False,failure=str(error))
        if not all(c['passed'] for c in checks.values()): result['status']='blocked'
        write(output/'integrity.json',dict(before=before,tools=identities,final_checks=checks))
        write(output/'assessment.json',result)
        (output/'ASSESSMENT.md').write_text('Status: '+result['status']+'\n\n'+result.get('failure','')+'\n\nDiagnostic only. Incremental overhead unmeasured; exact queue insertion unavailable.\n')
        o.seal(output)
    return result


def command(argv, output, name, timeout=30, env=None, credentials=None):
    with (output/(name+'.stdout')).open('x') as stdout,(output/(name+'.stderr')).open('x') as stderr:
        done=subprocess.run(argv,stdout=stdout,stderr=stderr,timeout=timeout,env=env,**(credentials or {}))
    write(output/(name+'.command.json'),dict(argv=argv,exit=done.returncode))
    require(done.returncode==0,'command failed: '+name)
    return (output/(name+'.stdout')).read_text()


def record_argv(target):
    return ['perf','record','--all-cpus','--clockid','CLOCK_MONOTONIC','--mmap-pages','256','--timestamp','--sample-cpu','--raw-samples','--no-buildid','--no-buildid-cache','-o',str(target), *[x for event in EVENTS for x in ('-e','sched:'+event)]]


def clock_header(header):
    # PERF_HEADER_CLOCKID and all recorded event attributes must agree.
    attributes=re.findall(r'\bclockid\s*=\s*(\d+)',header)
    summary=re.search(r'clockid\s*:\s*(?:1\b|CLOCK_MONOTONIC\b|monotonic\s*\(1\))',header,re.I)
    require((attributes and all(value=='1' for value in attributes)) or summary,'recorder CLOCK_MONOTONIC metadata missing')
    require(not attributes or all(value=='1' for value in attributes),'conflicting recorder clock metadata')


def verify_preparation(package):
    o.check_output(package)
    require(read(package/'assessment.json')['status']=='prepared','preparation blocked')
    o.verify(PREPARED); o.check_output(GAP); o.check_output(HISTORICAL)
    p.verify_generated(package,PREPARED)
    return o.inventory(package)


def preflight(package,output):
    def run(result):
        verify_preparation(package)
        fixtures=o.fixture_hashes(); fixture=str(o.old.FIXTURE_ROOT/'160x80.png')
        require(fixture in fixtures,'fixture missing')
        write(output/'fixtures.json',{fixture:fixtures[fixture]})
        write(output/'host.json',dict(kernel=list(os.uname()),boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),feasibility=p.feasibility()))
        # Verify the recorded installer, rather than the historically mismatching live tool.
        expected=read(PREPARED/'input-integrity.json')['before']
        snapshots={str(INSTALLER/name):expected[str(INSTALLER/name)] for name in ('manage-images-generations.py','install_state.py')}
        o.gate.smoke.verify_hashes(Path('/'),snapshots); write(output/'installer.json',snapshots)
        command(['perf','--version'],output,'perf-version')
        help_result=subprocess.run(['perf','record','-h'],capture_output=True,text=True,timeout=5)
        help_text=help_result.stdout+help_result.stderr
        (output/'perf-record-help.txt').write_text(help_text)
        require(all(option in help_text for option in ('--clockid','--control','--all-cpus','--mmap-pages')),'required perf options missing')
        command(['pkg-config','--modversion','Qt6Core','libexif','libwebp'],output,'dependencies')
        formats={}; failures=[]
        for event in EVENTS:
            path=Path('/sys/kernel/tracing/events/sched')/event/'format'
            try: formats[event]=path.read_text()
            except OSError as error: failures.append(dict(path=str(path),failure=str(error)))
        write(output/'tracepoint-formats.json',dict(formats=formats,failures=failures))
        require(not failures,'scheduler tracepoint formats inaccessible')
        required_fields=dict(sched_switch=('prev_pid','next_pid','prev_state'),sched_wakeup=('pid','target_cpu'),sched_wakeup_new=('pid','target_cpu'),sched_process_fork=('parent_pid','child_pid'),sched_process_exec=('pid','old_pid'),sched_process_exit=('pid',))
        for event,fields in required_fields.items():
            require(all(re.search(r'field:[^;]*\b'+field+r'\s*;',formats[event]) for field in fields),'tracepoint schema mismatch: '+event)
        boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        clock=dict(name='CLOCK_MONOTONIC',provenance=dict(boot_id=boot,host=Path('/etc/machine-id').read_text().strip()))
        write(output/'clock.json',clock)
        _,metadata=capture(output,lambda remaining: None)
        metadata['clock']=clock
        write(output/'recording-metadata.json',metadata)
        exported=(output/'perf-export.stdout').read_text()
        normalized=n.normalize(exported,metadata,(),str(output/'perf-export.stdout'))
        write(output/'scheduler.json',normalized)
        require(normalized['export_complete'] and not any(e['kind']=='loss' for e in normalized['events']),'rehearsal export incomplete or capture loss')
        env,credentials=session(); scope=o.gate.scope_snapshot(1000,env,credentials)
        write(output/'scopes.json',scope); require(scope['isolated'],'initial isolation unverified')
        result['status']='ready'
    return sealed_action(output,[package,PREPARED,GAP,HISTORICAL,INSTALLER],run)


def ready(preflight_path,package):
    o.check_output(preflight_path)
    require(read(preflight_path/'assessment.json')['status']=='ready','preflight blocked')
    require(read(preflight_path/'integrity.json')['before'][str(package)]==verify_preparation(package),'preparation drift since preflight')
    clock=read(preflight_path/'clock.json')
    require(clock['provenance']['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'boot drift')
    o.gate.smoke.verify_hashes(Path('/'),read(preflight_path/'installer.json'))
    o.gate.smoke.verify_hashes(Path('/'),read(preflight_path/'fixtures.json'))
    host=read(preflight_path/'host.json')
    require(host['kernel']==list(os.uname()) and host['feasibility']['identities']==p.feasibility()['identities'],'host dependency identity drift')


def build(package,preflight_path,output):
    def run(result):
        ready(preflight_path,package)
        saved_path=o.old.NATIVE/'commands.json'
        require(o.digest(saved_path)==read(o.old.NATIVE/'evidence-hashes.json')['commands.json'],'recipe drift')
        original=o.old.NATIVE/'B'; base=output/'B'; base.mkdir()
        commands=[]
        for row in read(saved_path):
            if not any(str(original)+'/' in arg for arg in row['argv']): continue
            argv=[]
            for arg in row['argv']:
                arg=arg.replace(str(original),str(base))
                for group in o.prep.GROUPS: arg=arg.replace(str(base/group),str(package/'B'/group))
                argv.append(arg)
            if argv[:2]==['cmake','--build']:
                require('--parallel' in argv and argv[argv.index('--parallel')+1]=='4','recipe jobs mismatch')
            commands.append(argv); write(output/'build-commands.json',commands)
            command(argv,base,'build-'+str(len(commands)),timeout=600)
        require(commands,'empty build recipe')
        write(base/'package-resolution.json',o.providers(base)); o.bundles(base)
        for label,relative in (('helper','build/holonight-images/holonight-images-helper'),('harness','reuse-harness/preview-benchmark')):
            linkage=command(['ldd',str(base/relative)],base,label+'-linkage')
            require('not found' not in linkage,'unresolved linkage')
            symbols=command(['nm','-C',str(base/relative)],base,label+'-symbols')
            require('StandbyTrace::' in symbols and (label!='harness' or 'SchedulerTrace::' in symbols and 'DeliveryTrace::' in symbols),'probe linkage missing')
        dispatch_test(package,output)
        result['status']='built'
    return sealed_action(output,[package,preflight_path],run)


def dispatch_test(package,output):
    source=output/'dispatch-test.cpp'
    source.write_text('#include "'+str(package/'B/trace.h')+'"\n'+r'''
#include <cassert>
#include <stdexcept>
struct Receiver : QObject {
  SchedulerTrace::Application* app;
  int depth=0; bool throws=false; bool result=true;
  bool event(QEvent* e) override {
    assert(e->type()==QEvent::MetaCall);
    auto id=SchedulerTrace::dispatch; assert(id);
    if (!depth++) { QEvent nested(QEvent::MetaCall); assert(app->notify(this,&nested)); assert(SchedulerTrace::dispatch==id); }
    --depth;
    if (throws) throw std::runtime_error("propagated");
    return depth ? true : result;
  }
};
int main(int argc,char** argv) {
  SchedulerTrace::Application app(argc,argv); Receiver r; r.app=&app;
  QEvent event(QEvent::MetaCall);
  auto before=DeliveryTrace::sequence.load();
  assert(app.notify(&r,&event)); assert(!SchedulerTrace::dispatch);
  r.result=false; assert(!app.notify(&r,&event)); assert(!SchedulerTrace::dispatch);
  r.throws=true; bool caught=false;
  try { app.notify(&r,&event); } catch(const std::runtime_error&) { caught=true; }
  assert(caught && !SchedulerTrace::dispatch && before==DeliveryTrace::sequence.load());
}
''')
    flags=command(['pkg-config','--cflags','--libs','Qt6Core'],output,'dispatch-flags').split()
    command(['c++','-std=c++20','-fPIC',str(source),'-o',str(output/'dispatch-test'),*flags],output,'dispatch-build')
    command([str(output/'dispatch-test')],output,'dispatch-native')


def supplemental(target,name):
    records=[]
    for path in (target.with_suffix('.stderr'),target.with_suffix('.stdout')):
        for number,line in enumerate(path.read_text().splitlines(),1):
            if line.startswith('SCHEDULER '): records.append(dict(json.loads(line[len('SCHEDULER '):]),invocation=name,file=str(path),line=number,text=line))
    return records


def run_workload(target,count,runtime,built,clock,timeout=30):
    env,credentials=session()
    argv=[str(built/'B/reuse-harness/preview-benchmark'),str(runtime/'B'),str(o.old.FIXTURE_ROOT/'160x80.png'),'startup',str(count),str(target)]
    write(target.with_suffix('.command.json'),dict(argv=argv,clock=clock,binary_sha256=o.digest(Path(argv[0])),fixture_sha256=o.digest(Path(argv[2])),built_seal=o.digest(built/'seal.json'),source_provenance=o.digest(built/'integrity.json')))
    process=o.gate.smoke.execute(argv,target,env,credentials,timeout=timeout)
    write(target.with_suffix('.process.json'),process)
    return process


def validate_invocation(target,count,process,clock):
    env,credentials=session()
    row=dict(mode='v4',variant='B',fixture='160x80.png',observations=count)
    o.validate(target,row,process,1000)
    records=supplemental(target,target.stem)
    inv=[dict(invocation=target.stem,clock=clock,accounting=read(target.with_suffix('.v4.json')))]
    linked=a.account(inv,records)
    require(not linked['issues'] and all(r['link_status']=='linked' for r in linked['rows']),'supplemental linkage failed')
    after=o.gate.scope_snapshot(1000,env,credentials)
    write(target.with_suffix('.scopes-after.json'),after); require(after['isolated'],'cleanup isolation failed')
    return inv,records


def isolated(target):
    env,credentials=session()
    before=o.gate.scope_snapshot(1000,env,credentials)
    write(target.with_suffix('.scopes-before.json'),before); require(before['isolated'],'scope isolation failed')


def acknowledge(fd,recorder,target):
    # perf evlist__ctlfd_ack writes sizeof("ack\n"), including the NUL.
    # Retain bytes even when the protocol or readiness check fails.
    deadline=time.monotonic()+5; data=b''
    write(target/'recorder-ack.json',dict(hex=''))
    while b'\n' not in data:
        require(recorder.poll() is None,'recorder exited before acknowledgement')
        require(select.select([fd],[],[],max(0,deadline-time.monotonic()))[0],'recorder readiness timeout')
        chunk=os.read(fd,64); data+=chunk
        write(target/'recorder-ack.json',dict(hex=data.hex()))
        require(chunk and len(data)<=5,'recorder readiness failed')
    require(data in (b'ack\n',b'ack\n\0') and recorder.poll() is None,'recorder readiness failed')


def shutdown(recorder,ready=False):
    # One deadline includes escalation and explicit child reaping.
    deadline=time.monotonic()+5
    result=dict(passed=False,reaped=False,forced=False,timed_out=False,sigint_sent=False)
    try:
        if recorder.poll() is None:
            recorder.send_signal(signal.SIGINT)
            result['sigint_sent']=True
        try:
            code=recorder.wait(timeout=max(0,deadline-time.monotonic()-1))
        except subprocess.TimeoutExpired:
            result.update(forced=True,timed_out=True)
            os.killpg(recorder.pid,signal.SIGKILL)
            code=recorder.wait(timeout=max(0,deadline-time.monotonic()))
        result.update(reaped=True,exit=code)
        result['passed']=not result['timed_out'] and (code==0 or (ready and result['sigint_sent'] and code==-signal.SIGINT)) and time.monotonic()<=deadline
        if not result['passed']: result['failure']='recorder finalization timeout' if result['timed_out'] else 'recorder failed'
    except ERRORS as error:
        result['failure']=str(error)
    return result


def capture(target,work,*,bounds=None,export_env=None,export_credentials=None):
    ctl_r,ctl_w=os.pipe(); ack_r,ack_w=os.pipe(); recorder=None; cleanup=None
    boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    started=time.monotonic(); start_ns=time.monotonic_ns()
    argv=[*record_argv(target/'perf.data'),'--delay','-1','--control',f'fd:{ctl_r},{ack_w}']
    write(target/'record-command.json',dict(argv=argv,bounds=BOUNDS if bounds is None else bounds,boot=boot))
    try:
        with (target/'recorder.stdout').open('x') as stdout,(target/'recorder.stderr').open('x') as stderr:
            recorder=subprocess.Popen(argv,stdout=stdout,stderr=stderr,pass_fds=(ctl_r,ack_w),start_new_session=True)
            identity=Path('/proc')/str(recorder.pid)
            write(target/'recorder-process.json',dict(pid=recorder.pid,stat=(identity/'stat').read_text() if identity.exists() else None,argv=argv))
            os.close(ctl_r); ctl_r=None; os.close(ack_w); ack_w=None
            os.write(ctl_w,b'enable\n')
            acknowledge(ack_r,recorder,target)
            write(target/'recorder-readiness.json',dict(start_ns=start_ns,ready_ns=time.monotonic_ns(),pid=recorder.pid))
            value=work(max(0,30-(time.monotonic()-started)))
            require(time.monotonic()-started<=30,'capture session timeout')
            cleanup=shutdown(recorder,ready=True)
            write(target/'recorder-shutdown.json',cleanup)
            require(cleanup['passed'],cleanup.get('failure','recorder cleanup failed'))
            stop_ns=time.monotonic_ns()
        readers={}
        if export_env is not None: readers['env']=export_env
        if export_credentials is not None: readers['credentials']=export_credentials
        header=command(['perf','report','--header-only','--stdio','-i',str(target/'perf.data')],target,'recording-header',**readers)
        command(['perf','script','--ns','--show-task-events','--show-lost-events','-F','comm,pid,tid,cpu,time,event,trace','-i',str(target/'perf.data')],target,'perf-export',**readers)
        clock_header(header)
        require(all('sched:'+event in header for event in EVENTS),'recorded tracepoint missing')
        require(boot==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'boot changed during capture')
        return value,dict(start_ns=start_ns,stop_ns=stop_ns,boot_before=boot,boot_after=boot,clock_verified=True,header_file=str(target/'recording-header.stdout'))
    finally:
        original_error=sys.exc_info()[0] is not None
        try:
            if recorder is not None and cleanup is None:
                cleanup=shutdown(recorder)
                write(target/'recorder-shutdown.json',cleanup)
            if cleanup is None: cleanup=dict(passed=True,reaped=True,not_started=True)
            write(target/'recording-partial.json',dict(start_ns=start_ns,final_check_ns=time.monotonic_ns(),boot_before=boot,boot_after=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),clock_verified=False,cleanup=cleanup))
        except ERRORS as error:
            cleanup=dict(passed=False,failure=str(error))
            write(target/'recording-cleanup-failure.json',cleanup)
        finally:
            for fd in (ctl_r,ctl_w,ack_r,ack_w):
                if fd is not None: os.close(fd)
        if not original_error: require(cleanup['passed'],cleanup.get('failure','recorder cleanup failed'))


def execute(package,preflight_path,built,output):
    def run(result):
        require(os.geteuid()==0,'managed runtime staging requires privileged wrapper')
        ready(preflight_path,package); o.check_output(built)
        require(read(built/'assessment.json')['status']=='built','build blocked')
        require(read(built/'integrity.json')['before'][str(package)]==o.inventory(package) and read(built/'integrity.json')['before'][str(preflight_path)]==o.inventory(preflight_path),'build input provenance mismatch')
        marker=built.parent/(built.name+'-execution-started.json')
        with marker.open('x') as stream: json.dump(dict(output=str(output),built_seal=o.digest(built/'seal.json')),stream)
        runtime=Path('/run')/('holonight-delivery-scheduler-'+output.name)
        require(not runtime.exists() and not runtime.is_symlink(),'runtime destination reused')
        runtime.mkdir(mode=0o755)
        write(output/'runtime.json',dict(path=str(runtime)))
        env,credentials=session()
        stage=[sys.executable,'-B',str(INSTALLER/'manage-images-generations.py'),'install','--runtime',str(runtime/'B'),'--source',str(built/'B/runtime'),'--helper',str(built/'B/build/holonight-images/holonight-images-helper')]
        protected=None
        try:
            command(stage,output,'installer',env=env)
            o.gate.staged_payloads(built,runtime,'B')
            protected=o.gate.protected_inventory(runtime); write(output/'runtime-before.json',protected)
            targets=o.gate.observation_directory(output,1000,pwd.getpwuid(1000).pw_gid)
            clock=read(preflight_path/'clock.json')
            def integrity():
                ready(preflight_path,package); o.check_output(built)
                require(o.gate.protected_inventory(runtime)==protected,'runtime drift')
            integrity()
            isolated(targets/'uncaptured.json')
            process=run_workload(targets/'uncaptured.json',1,runtime,built,clock)
            validate_invocation(targets/'uncaptured.json',1,process,clock)
            integrity()
            isolated(targets/'captured.json')
            def work(remaining):
                # Timeout covers readiness plus the workload, not just observation work.
                require(remaining>0,'capture session timeout')
                return run_workload(targets/'captured.json',10,runtime,built,clock,timeout=min(30,remaining))
            process,metadata=capture(output,work)
            metadata['clock']=clock; write(output/'recording-metadata.json',metadata)
            integrity()
            inv,records=validate_invocation(targets/'captured.json',10,process,clock)
            write(output/'accounting.json',inv); write(output/'supplemental.json',records)
            identities=records+[e for v in inv for e in v['accounting']['events']]
            write(output/'task-identities.json',identities)
            normalized=n.normalize((output/'perf-export.stdout').read_text(),metadata,identities,str(output/'perf-export.stdout'))
            write(output/'scheduler.json',normalized)
            analysis=a.account(inv,records,normalized); write(output/'analysis.json',analysis)
            require(analysis['attribution_complete'],'scheduler attribution incomplete')
            result['status']='complete'
        finally:
            checks={}
            for name,action in [('runtime',lambda:require(o.gate.protected_inventory(runtime)==protected,'runtime drift')),('scopes',lambda:require(o.gate.scope_snapshot(1000,env,credentials)['isolated'],'final scopes unverified'))]:
                try: action(); checks[name]=dict(passed=True)
                except ERRORS as error: checks[name]=dict(passed=False,failure=str(error))
            write(output/'execution-final-checks.json',checks)
            if not all(c['passed'] for c in checks.values()): result['status']='blocked'
    return sealed_action(output,[package,preflight_path,built],run)


def report(evidence,output):
    def run(result):
        o.check_output(evidence)
        assessment=read(evidence/'assessment.json')
        if assessment.get('failure'): result['failure']=assessment['failure']
        consumed=read(evidence/'integrity.json')['before']
        checked={}
        for name,expected in consumed.items():
            path=Path(name)
            require(path.absolute()==path.resolve(),'consumed source symlink')
            require(o.inventory(path)==expected,'independent consumed input drift: '+name)
            if (path/'seal.json').exists(): o.check_output(path)
            # Historical preparation predates the corrected dispatch counter.
            # Its consumed inventory/seal is verified above, without rewriting it.
            if (path/'anchors.json').exists() and path!=HISTORICAL: p.verify_generated(path,PREPARED)
            checked[name]=dict(passed=True)
        write(output/'independent-input-verification.json',checked)
        write(output/'evidence.json',dict(path=str(evidence),seal=o.digest(evidence/'seal.json'),assessment=assessment))
        if (evidence/'perf.data').exists():
            command(['perf','script','--ns','--show-task-events','--show-lost-events','-F','comm,pid,tid,cpu,time,event,trace','-i',str(evidence/'perf.data')],output,'retained-perf-export')
            header=command(['perf','report','--header-only','--stdio','-i',str(evidence/'perf.data')],output,'retained-recording-header')
            clock_header(header)
        target=evidence/'observations/uncaptured.json'
        if target.exists():
            row=dict(mode='v4',variant='B',fixture='160x80.png',observations=1)
            o.validate(target,row,read(target.with_suffix('.process.json')),1000,replay=True)
            records=supplemental(target,target.stem)
            clock=read(target.with_suffix('.command.json'))['clock']
            inv=[dict(invocation=target.stem,clock=clock,accounting=read(target.with_suffix('.v4.json')))]
            linkage=a.account(inv,records)
            require(not linkage['issues'] and all(row['link_status']=='linked' for row in linkage['rows']),'independent uncaptured linkage failed')
            write(output/'uncaptured-linkage.json',linkage)
        runtime=evidence/'runtime.json'
        if runtime.exists() and (evidence/'runtime-before.json').exists():
            require(o.gate.protected_inventory(Path(read(runtime)['path']))==read(evidence/'runtime-before.json'),'independent runtime drift')

        if (evidence/'recording-partial.json').exists() and not (evidence/'recording-metadata.json').exists() and target.exists():
            partial=read(evidence/'recording-partial.json')
            metadata=dict(start_ns=partial['start_ns'],stop_ns=partial['final_check_ns'],boot_before=partial['boot_before'],boot_after=partial['boot_after'],clock=read(target.with_suffix('.command.json'))['clock'],clock_verified=True)
            write(output/'partial-recording-metadata.json',metadata)
            normalized=n.normalize((output/'retained-perf-export.stdout').read_text(),metadata,(),str(output/'retained-perf-export.stdout'))
            write(output/'partial-scheduler.json',normalized)
        if (evidence/'analysis.json').exists():
            normalized=n.normalize((evidence/'perf-export.stdout').read_text(),read(evidence/'recording-metadata.json'),read(evidence/'task-identities.json'),str(evidence/'perf-export.stdout'))
            require(normalized==read(evidence/'scheduler.json'),'normalization replay mismatch')
            replay=a.account(read(evidence/'accounting.json'),read(evidence/'supplemental.json'),read(evidence/'scheduler.json'))
            require(json.loads(json.dumps(replay))==read(evidence/'analysis.json'),'analysis replay mismatch')
        result.update(status=assessment['status'],failure=assessment.get('failure',''),evidence=str(evidence))
        captured=(evidence/'observations/captured.json').exists()
        (output/'REPORT.md').write_text('Status: '+result['status']+'\n\n'+result.get('failure','')+'\n\nUncaptured observations: '+str(int(target.exists()))+'. Captured invocation completed: '+str(captured)+'.\n\nNo retries or expanded fixtures. Raw recording and nanosecond export retained. A partial recorder session is not a captured preview workload.\n\nIndependent source reconstruction, consumed-input seals, uncaptured accounting replay, runtime inventory, final scope and residual-process checks are retained separately. Exact queue insertion remains unavailable. Overlapping thread and endpoint views are non-additive. Non-runnable time identifies no blocking cause. Incremental overhead remains unmeasured.\n')
    return sealed_action(output,[evidence],run)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('preflight','build','execute','report'))
    parser.add_argument('--prepared',type=Path,required=True); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--preflight',type=Path); parser.add_argument('--built',type=Path); parser.add_argument('--evidence',type=Path)
    args=parser.parse_args()
    if args.action=='preflight': result=preflight(args.prepared,args.output)
    elif args.action=='build': result=build(args.prepared,args.preflight,args.output)
    elif args.action=='execute': result=execute(args.prepared,args.preflight,args.built,args.output)
    else: result=report(args.evidence,args.output)
    print(json.dumps(result)); sys.exit(result['status'] not in ('ready','built','complete'))
