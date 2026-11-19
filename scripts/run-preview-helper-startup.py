#!/usr/bin/env python3
"""Bounded private A/C helper-startup diagnostic. A failed gate stops the schedule."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    value=importlib.util.module_from_spec(spec); spec.loader.exec_module(value); return value

v=module('helper_prepare','prepare-preview-helper-startup.py')
independent=module('helper_seal_checker','verify-preview-helper-startup.py')
r=module('run_validation_recorder','run-preview-delivery-scheduler.py')
o,require,read,write=v.o,v.require,v.read,v.write
ERRORS=r.ERRORS
KEYS=[(mode,variant) for mode in ('baseline','instrumented') for variant in ('A','C')]


def ordinal_mapping(manifest):
    require(isinstance(manifest.get('files'),list),'manifest files unavailable')
    rows=[]; paths=set()
    for ordinal,record in enumerate(manifest['files']):
        name=record['path']; size=record['size']
        require(isinstance(name,str) and name.startswith('usr/') and '..' not in Path(name).parts and name not in paths,
                'invalid manifest path')
        require(type(size) is int and size>=0,'invalid manifest size')
        paths.add(name); rows.append(dict(ordinal=ordinal,path=name,size=size,sha256=record['sha256']))
    return rows


def build_commands(package,output):
    commands=o.old.NATIVE/'commands.json'
    require(o.digest(commands)==read(o.old.NATIVE/'evidence-hashes.json')['commands.json'],'native recipe identity drift')
    saved=read(commands); result=[]
    for mode,variant in KEYS:
        original=o.old.NATIVE/variant; target=output/mode/variant
        selected=[row['argv'] for row in saved if any(str(original)+'/' in arg for arg in row['argv'])]
        require(selected,'empty native build sequence')
        for argv in selected:
            transformed=[]
            for arg in argv:
                arg=arg.replace(str(original),str(target))
                for group in v.GROUPS:
                    arg=arg.replace(str(target/group),str(package/mode/variant/group))
                transformed.append(arg)
            if transformed[:2]==['cmake','--build']:
                require('--parallel' in transformed and transformed[transformed.index('--parallel')+1]=='4','native build jobs drift')
            result.append(dict(mode=mode,variant=variant,argv=transformed))
    return result


def build(package,output):
    def run(result):
        require(os.geteuid()!=0,'build must run as desktop user')
        check_package(package)
        preflight(package,output)
        commands=build_commands(package,output)
        write(output/'commands.json',commands)
        write(output/'environment.json',dict(host=list(os.uname()),jobs=4))
        for name,argv in [('compiler',['c++','--version']),('dependencies',['pkg-config','--modversion','Qt6Core','libexif','libwebp']),
                          ('cmake',['cmake','--version']),('ninja',['ninja','--version'])]:
            r.command(argv,output,name+'-version')
        for mode,variant in KEYS:
            check_package(package)
            base=output/mode/variant; base.mkdir(parents=True)
            for index,row in enumerate(x for x in commands if (x['mode'],x['variant'])==(mode,variant)):
                r.command(row['argv'],base,'build-'+str(index),timeout=600)
            write(base/'package-resolution.json',o.providers(base)); o.bundles(base)
            write(base/'manifest-ordinals.json',ordinal_mapping(read(base/'runtime/manifest.json')))
            for label,relative in [('helper','build/holonight-images/holonight-images-helper'),('harness','reuse-harness/preview-benchmark')]:
                binary=base/relative
                linkage=r.command(['ldd',str(binary)],base,label+'-linkage')
                require('not found' not in linkage,'unresolved native linkage')
                symbols=r.command(['nm','-C',str(binary)],base,label+'-symbols')
                require('StandbyTrace::' in symbols,'original tracing missing')
                if label=='harness': require('DeliveryTrace::' in symbols,'v4 tracing missing')
                # Helper preparation is linked into the harness through installed providers.
                if label=='harness': require(('HelperStartupTrace::' in symbols)==(mode=='instrumented'),'helper-startup probe linkage mismatch')
                write(base/(label+'-identity.json'),dict(path=str(binary),sha256=o.digest(binary),linkage=linkage))
            print(mode,variant,'built',flush=True)
        check_package(package)
        result['status']='built'
    return action(output,[package],run)


def stage_worker(request,output):
    require(os.geteuid()==0,'staging requires scoped elevation')
    config=read(request); built=Path(config['built']); mode=config['mode']; variant=config['variant']
    require((mode,variant) in KEYS,'unknown staging configuration')
    o.check_output(built)
    require(read(built/'assessment.json')['status']=='built' and o.digest(built/'seal.json')==config['built_seal'],'staging build drift')
    require(output.absolute()==output.resolve() and output.parents[2]==Path('/run') and
            output.parent.name==mode and output.name==variant and output.parents[1].name.startswith('holonight-helper-startup-'),
            'invalid protected staging destination')
    root=output.parents[1]
    owner=dict(built=str(built),seal=config['built_seal'],execution=config['execution'])
    if root.exists():
        o.gate.protected_inventory(root)
        require(read(root/'diagnostic-owner.json')==owner,'protected staging root collision')
    else:
        root.mkdir(mode=0o755)
        write(root/'diagnostic-owner.json',owner)
    output.parent.mkdir(mode=0o755,exist_ok=True)
    require(not output.exists() and not output.is_symlink(),'staging destination reused')
    base=built/mode/variant
    if variant=='A':
        shutil.copytree(base/'runtime',output)
    else:
        installer=Path(config['installer'])
        require(installer==r.INSTALLER/'manage-images-generations.py' and
                o.digest(installer)==config['installer_sha256'],'staging installer drift')
        for name,digest in config['installer_hashes'].items(): require(o.digest(Path(name))==digest,'staging support drift')
        r.command([sys.executable,'-B',str(installer),'install','--runtime',str(output),
                   '--source',str(base/'runtime'),'--helper',str(base/'build/holonight-images/holonight-images-helper')],
                  request.parent,'install-'+mode+'-'+variant,timeout=120)
    o.staged(built/mode,output.parent,variant)



def check_package(package):
    checker=module('helper_host_checker','verify-preview-helper-startup-host.py') if (package/'host-rebind.json').exists() else independent
    verification=checker.verify(package)
    binding=package.parent/(package.name+'-independent.json')
    record=read(binding)
    require(record==verification,'independent preparation verification binding mismatch')
    require(read(package/'protocol.json')==v.protocol(),'frozen protocol drift')
    for name,digest in read(package/'fixtures.json').items():
        require(o.digest(Path(name))==digest,'fixture drift')
    return o.inventory(package)


def identities():
    names=('run-preview-helper-startup.py','report-preview-helper-startup.py',
           'verify-preview-helper-startup-run.py','analyze-preview-helper-startup.py',
           'verify-preview-helper-startup.py','prepare-preview-helper-startup.py',
           'run-preview-validation.py','run-preview-delivery-scheduler.py',
           'normalize-preview-delivery-perf.py','measure-preview-delivery-overhead.py')
    names+=('rebind-preview-helper-startup.py','verify-preview-helper-startup-host.py')
    return {str(path):o.digest(path) for path in
            [*(ROOT/'scripts'/name for name in names),ROOT/'tests/test_preview_helper_startup_run.py']}


def action(output,inputs,work):
    require(os.geteuid()!=0,'orchestration and offline analysis must run as desktop user')
    o.fresh(output,*inputs)
    result=dict(status='blocked',launched=0,unexecuted=36,invocations=[],
                measured_observations=0,warmup_observations=0)
    before={}; tools=identities()
    try:
        snapshots=output/'tools'; snapshots.mkdir()
        for name in tools: shutil.copy2(name,snapshots/Path(name).name)
        before={str(path):o.inventory(path) for path in inputs}
        work(result)
    except ERRORS as error: result['failure']=str(error)
    finally:
        checks={}
        for name,expected in before.items():
            try: checks[name]=o.inventory(Path(name))==expected
            except OSError: checks[name]=False
        for name,expected in tools.items():
            try: checks[name]=o.digest(Path(name))==expected
            except OSError: checks[name]=False
        if not all(checks.values()): result.update(status='blocked',integrity_failure='input/tool drift')
        write(output/'integrity.json',dict(before=before,tools=tools,checks=checks,passed=all(checks.values())))
        write(output/'assessment.json',result)
        write(output/'unexecuted-schedule.json',v.protocol()['schedule'][result['launched']:])
        (output/'ASSESSMENT.md').write_text('# Private helper-startup diagnostic\n\nStatus: '+result['status']+
            '\n\n'+result.get('failure','')+'\n\nNo optimization selected. Qualification remains failed at 78/80 gates.\n')
        o.seal(output)
    return result


def clock_identity():
    import socket
    return dict(name='CLOCK_MONOTONIC',provenance=dict(host=socket.gethostname(),
                boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()))


def elevated(argv,output,name,timeout=100):
    return r.command(['sudo','-A',*argv],output,name,timeout=timeout)


def record(output,label,clock,entry=None):
    directory=output/('recording-'+label); directory.mkdir()
    (directory/'perf.data').touch(mode=0o600,exist_ok=False)
    request=output/(label+'-recorder-request.json')
    write(request,dict(entry=entry,clock=clock))
    argv=[sys.executable,'-B',str(Path(__file__).resolve()),'record','--request',str(request),'--output',str(directory)]
    elevated(argv,output,'recorder-'+label)
    normalize_recording(directory,entry)
    return read(directory/'workload-process.json') if entry else None


def preflight(package,output):
    """Exactly one workload-free rehearsal, before any compiler invocation."""
    check_package(package)
    env,credentials=r.session()
    clock=clock_identity()
    write(output/'host.json',dict(hostname=clock['provenance']['host'],
        machine_id=Path('/etc/machine-id').read_text().strip(),boot_id=clock['provenance']['boot_id'],kernel=list(os.uname())))
    argv=[sys.executable,'-B',str(Path(__file__).resolve()),'record','--request',
          str(output/'rehearsal-recorder-request.json'),'--output',str(output/'recording-rehearsal')]
    write(output/'preflight-preregistration.json',dict(protocol=v.protocol(),clock=clock,environment=env,
        credentials=credentials,argv=['sudo','-A',*argv],perf_argv=r.record_argv(output/'recording-rehearsal/perf.data'),
        fixture_hashes=read(package/'fixtures.json'),preparation_seal=o.digest(package/'seal.json')))
    try:
        r.isolated(output/'initial.json')
        r.command(['perf','--version'],output,'perf-version')
        record(output,'rehearsal',clock)
        require(clock_identity()==clock,'host/boot drift')
        check_package(package)
        write(output/'preflight.json',dict(status='ready',clock=clock))
    finally:
        checks={}
        for name,check in [('isolation',lambda:r.isolated(output/'final.json')),
                           ('residuals',lambda:r.residuals(output)),('inputs',lambda:check_package(package))]:
            try: check(); checks[name]=dict(passed=True)
            except ERRORS as error: checks[name]=dict(passed=False,failure=str(error))
        write(output/'preflight-final-checks.json',checks)
        require(all(c['passed'] for c in checks.values()),'preflight final cleanup/integrity failed')


def planned_commands(built,runtime,targets):
    result=[]
    for index,row in enumerate(v.protocol()['schedule']):
        mode='baseline' if row['arm']=='baseline' else 'instrumented'
        invocation=targets.parent.name+f'-{index:03}'
        result.append(dict(invocation=row,identity=invocation,argv=[
            str(built/mode/row['variant']/'reuse-harness/preview-benchmark'),str(runtime/mode/row['variant']),
            str(o.old.FIXTURE_ROOT/row['fixture']),'startup',str(row['observations']),str(targets/f'{index:03}.json')]))
    return result


def run_schedule(commands,output,result,integrity,before,launch,account):
    require([e['invocation'] for e in commands]==v.protocol()['schedule'],'scheduled invocation drift')
    require(len({e['identity'] for e in commands})==36 and all(e['identity'] for e in commands),'invocation identity collision')
    for index,entry in enumerate(commands):
        integrity(); before(Path(entry['argv'][-1]))
        saved=dict(index=index,entry=entry,status='failed')
        result['invocations'].append(saved); result.update(launched=index+1,unexecuted=35-index)
        write(output/'progress.json',result)
        process=launch(index,entry)
        samples=account(index,entry,process)
        require(len(samples)==entry['invocation']['observations'],'sample count mismatch')
        integrity()
        saved.update(status='passed',process=process,samples=samples)
        result['warmup_observations' if entry['invocation']['warmup'] else 'measured_observations']+=len(samples)
        write(output/'progress.json',result)
        print(index+1,'/36 passed',flush=True)
    require(result['measured_observations']==150 and result['warmup_observations']==6,'observation budget mismatch')


def workload(entry,timeout=30):
    env,credentials=r.session()
    # session() constructs a fresh environment after privilege dropping is selected.
    env['HOLONIGHT_HELPER_INVOCATION']=entry['identity']
    target=Path(entry['argv'][-1])
    write(target.with_suffix('.command.json'),dict(entry,environment=env,credentials=credentials))
    process=o.gate.smoke.execute(entry['argv'],target,env,credentials,timeout=timeout)
    write(target.with_suffix('.process.json'),process)
    return process


def recorder_worker(request,output):
    require(os.geteuid()==0,'recorder worker requires scoped elevation')
    configuration=read(request); clock=configuration['clock']; entry=configuration['entry']
    require(clock==clock_identity(),'recorder host/boot mismatch')
    require(output.is_dir() and output.absolute()==output.resolve(),'invalid recording directory')
    data=output/'perf.data'
    require(data.is_file() and not data.is_symlink() and data.stat().st_uid==1000 and data.stat().st_size==0,
            'recorder requires fresh desktop-owned evidence file')
    if entry:
        row=entry['invocation']
        require(row in v.protocol()['schedule'] and row['arm']=='captured','unregistered recorder workload')
        require(entry['identity'] and entry['argv'][2]==str(o.old.FIXTURE_ROOT/'3200x2400.png') and
                entry['argv'][3:5]==['startup',str(row['observations'])],'recorder workload drift')
    def work(remaining):
        require(remaining>0,'readiness exhausted capture budget')
        return workload(entry,min(30,remaining)) if entry else None
    env,credentials=r.session()
    process,metadata=r.capture(output,work,bounds=v.protocol(),export_env=env,export_credentials=credentials)
    metadata['clock']=clock
    write(output/'recording-metadata.json',metadata)
    if entry: write(output/'workload-process.json',process)


def normalize_recording(output,entry=None):
    a=module('helper_normalization_parser','analyze-preview-helper-startup.py')
    identities=[]
    if entry:
        target=Path(entry['argv'][-1])
        for path in (target.with_suffix('.stderr'),target.with_suffix('.stdout')):
            parsed,issues=a.parse(path.read_text(),str(path))
            require(not issues,'invalid supplemental identity evidence')
            identities.extend(parsed)
    write(output/'task-identities.json',identities)
    normalized=r.n.normalize((output/'perf-export.stdout').read_text(),read(output/'recording-metadata.json'),
                             identities,str(output/'perf-export.stdout'))
    write(output/'scheduler.json',normalized)
    require(normalized['export_complete'] and not normalized.get('diagnostics') and
            not any(e['kind']=='loss' for e in normalized['events']),'recorder loss/incomplete export')


def execute(package,built,output):
    def run(result):
        require(os.geteuid()==1000,'orchestration must run as desktop user')
        check_package(package); o.check_output(built)
        require(read(built/'assessment.json')['status']=='built','native build blocked')
        require(read(built/'integrity.json')['before'][str(package)]==o.inventory(package),'build provenance mismatch')
        require(read(built/'preflight.json')['clock']==clock_identity(),'preflight host/boot drift')
        require(read(built/'integrity.json')['tools']==identities(),'build tool drift')
        marker=built.parent/(built.name+'-execution-started.json')
        with marker.open('x') as stream: json.dump(dict(output=str(output),built=str(built)),stream)
        targets=output/'observations'; targets.mkdir()
        runtime=Path('/run')/('holonight-helper-startup-'+output.name)
        require(not runtime.exists() and not runtime.is_symlink(),'runtime destination reused')
        commands=planned_commands(built,runtime,targets)
        installer=r.INSTALLER/'manage-images-generations.py'
        snapshots=read(Path(read(package/'provenance.json')['prepared'])/'input-integrity.json')['before']
        hashes={str(r.INSTALLER/name):snapshots[str(r.INSTALLER/name)] for name in ('manage-images-generations.py','install_state.py')}
        stages=[]
        for mode,variant in KEYS:
            request=output/f'stage-{mode}-{variant}.json'
            config=dict(mode=mode,variant=variant,built=str(built),built_seal=o.digest(built/'seal.json'),
                execution=str(output),installer=str(installer),installer_sha256=o.digest(installer),installer_hashes=hashes)
            write(request,config)
            argv=[sys.executable,'-B',str(Path(__file__).resolve()),'stage','--request',str(request),'--output',str(runtime/mode/variant)]
            stages.append(dict(argv=argv,request=config,mode=mode,variant=variant))
        clock=clock_identity(); env,credentials=r.session()
        recorders=[]
        for index,entry in enumerate(commands):
            if entry['invocation']['arm']=='captured':
                label=f'{index:03}'
                recorders.append(dict(index=index,argv=['sudo','-A',sys.executable,'-B',str(Path(__file__).resolve()),
                    'record','--request',str(output/(label+'-recorder-request.json')),'--output',str(output/('recording-'+label))],
                    perf_argv=r.record_argv(output/('recording-'+label)/'perf.data')))
        write(output/'preregistration.json',dict(protocol=v.protocol(),commands=commands,staging=stages,recorders=recorders,
            clock=clock,environment=env,credentials=credentials,package=str(package),built=str(built),
            built_seal=o.digest(built/'seal.json'),protected_runtime=str(runtime),installer_hashes=hashes,
            fixture_hashes=read(package/'fixtures.json')))
        staged=[]; tool_identities=identities()
        def integrity():
            require(identities()==tool_identities,'execution tool drift')
            check_package(package); o.check_output(built)
            require(clock_identity()==clock,'host/boot drift')
            for name,digest in hashes.items(): require(o.digest(Path(name))==digest,'installer drift')
            for mode,variant,expected in staged:
                o.staged(built/mode,runtime/mode,variant)
                require(o.gate.protected_inventory(runtime/mode/variant)==expected,'staged payload drift')
        try:
            integrity(); r.isolated(targets/'initial.json')
            for stage in stages:
                mode,variant=stage['mode'],stage['variant']
                elevated(stage['argv'],output,f'stage-{mode}-{variant}',timeout=180)
                expected=o.staged(built/mode,runtime/mode,variant)
                staged.append((mode,variant,expected))
                write(output/'staged-inventories.json',[dict(mode=m,variant=v,inventory=i) for m,v,i in staged])
            reporter=module('helper_live_report','report-preview-helper-startup.py')
            def launch(index,entry):
                return record(output,f'{index:03}',clock,entry) if entry['invocation']['arm']=='captured' else workload(entry)
            def account(index,entry,process):
                target=Path(entry['argv'][-1])
                samples=o.validate(target,dict(entry['invocation'],mode='v4'),process,1000)
                reporter.invocation(package,entry,index,output)
                r.isolated(target.with_suffix('.after.json')); r.residuals(output)
                return samples
            run_schedule(commands,output,result,integrity,r.isolated,launch,account)
            result['status']='complete'
        finally:
            checks={}
            for name,check in [('integrity',integrity),('scopes',lambda:r.isolated(targets/'final.json')),
                               ('residuals',lambda:r.residuals(output))]:
                try: check(); checks[name]=dict(passed=True)
                except ERRORS as error: checks[name]=dict(passed=False,failure=str(error))
            write(output/'execution-final-checks.json',checks)
            require(all(c['passed'] for c in checks.values()),'execution final cleanup/integrity failed')
    return action(output,[package,built],run)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('build','execute','record','stage'))
    for name in ('prepared','built','request'): parser.add_argument('--'+name,type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    for name in ('prepared','built','request','output'):
        if getattr(args,name) is not None: setattr(args,name,getattr(args,name).absolute())
    if args.action=='stage': stage_worker(args.request,args.output); sys.exit(0)
    if args.action=='record': recorder_worker(args.request,args.output); sys.exit(0)
    require(args.prepared is not None,'--prepared required')
    result=build(args.prepared,args.output) if args.action=='build' else execute(args.prepared,args.built,args.output)
    print(json.dumps(result)); sys.exit(result['status'] not in ('built','complete'))
