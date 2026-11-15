#!/usr/bin/env python3
"""Bounded private A/C validation experiment. A failed gate stops the schedule."""
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

v=module('run_validation_prepare','prepare-preview-validation.py')
r=module('run_validation_recorder','run-preview-delivery-scheduler.py')
o,require,read,write=v.o,v.require,v.read,v.write
ERRORS=r.ERRORS
KEYS=[(mode,variant) for mode in ('baseline','validation') for variant in ('A','C')]


def check_package(package):
    o.check_output(package)
    require(read(package/'assessment.json')['status']=='prepared','validation preparation blocked')
    require(read(package/'protocol.json')==v.protocol(),'validation protocol drift')
    integrity=read(package/'integrity.json')
    require(integrity['passed'] and all(integrity['checks'].values()),'preparation integrity blocked')
    for name,digest in integrity['consumed'].items():
        require(o.digest(Path(name))==digest,'consumed preparation drift: '+name)
    for name,inv in integrity['before'].items():
        require(o.inventory(Path(name))==inv,'preparation provenance drift: '+name)
    return o.inventory(package)


def identities():
    names=('prepare-preview-validation.py','run-preview-validation.py','report-preview-validation.py','verify-preview-validation.py',
           'run-preview-delivery-scheduler.py','normalize-preview-delivery-perf.py',
           'analyze-preview-delivery-scheduler.py','measure-preview-delivery-overhead.py',
           'run-preview-delivery-smoke.py','run-preview-startup-smoke.py',
           'analyze-preview-delivery-tracing.py','analyze-preview-startup-v3.py',
           'analyze-preview-startup.py','measure-preview-tracing-overhead.py','measure-preview-reuse.py',
           'report-preview-predecode.py','report-preview-startup-bottlenecks.py')
    paths=[*(ROOT/'scripts'/n for n in names),ROOT/'tests/test_preview_validation.py']
    return {str(path):o.digest(path) for path in paths}


def action(output,inputs,work):
    require(os.geteuid()!=0,'build, orchestration and offline analysis must run without root')
    o.fresh(output,*inputs)
    result=dict(status='blocked'); before={}; tools=identities()
    try:
        snapshots=output/'tools'; snapshots.mkdir()
        for name in tools: shutil.copy2(name,snapshots/Path(name).name)
        before={str(p):o.inventory(p) for p in inputs}
        work(result)
    except ERRORS as error:
        result['failure']=str(error)
    finally:
        checks={}
        for name,inv in before.items():
            try: checks[name]=o.inventory(Path(name))==inv
            except OSError: checks[name]=False
        for name,digest in tools.items():
            try: checks[name]=o.digest(Path(name))==digest
            except OSError: checks[name]=False
        if not all(checks.values()): result.update(status='blocked',integrity_failure='input/tool drift')
        write(output/'integrity.json',dict(before=before,tools=tools,checks=checks,passed=all(checks.values())))
        write(output/'assessment.json',result)
        (output/'ASSESSMENT.md').write_text('# A/C validation experiment\n\nStatus: '+result['status']+'\n\n'+result.get('failure','')+
            '\n\nDiagnostic only. No retry, threshold change, overhead subtraction or C/D reassessment.\n')
        o.seal(output)
    return result


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
        commands=build_commands(package,output)
        write(output/'commands.json',commands)
        write(output/'environment.json',dict(host=list(os.uname()),jobs=4))
        for name,argv in [('compiler',['c++','--version']),('dependencies',['pkg-config','--modversion','Qt6Core','libexif','libwebp']),
                          ('cmake',['cmake','--version']),('ninja',['ninja','--version'])]:
            r.command(argv,output,name+'-version')
        for mode,variant in KEYS:
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
                # Runtime validation is linked into the harness through the installed providers.
                if label=='harness': require(('ValidationTrace::' in symbols)==(mode=='validation'),'validation probe linkage mismatch')
                write(base/(label+'-identity.json'),dict(path=str(binary),sha256=o.digest(binary),linkage=linkage))
            print(mode,variant,'built',flush=True)
        check_package(package)
        result['status']='built'
    return action(output,[package],run)


def planned_commands(built,runtime,targets):
    return [dict(invocation=row,argv=[str(built/row['mode']/row['variant']/'reuse-harness/preview-benchmark'),
                str(runtime/row['mode']/row['variant']),str(o.old.FIXTURE_ROOT/row['fixture']),
                'startup',str(row['observations']),str(targets/f'{index:03}.json')])
            for index,row in enumerate(v.schedule())]


def run_schedule(commands,output,result,integrity,before,launch,account):
    require([e['invocation'] for e in commands]==v.schedule(),'scheduled invocation drift')
    for index,entry in enumerate(commands):
        integrity(); target=Path(entry['argv'][-1]); before(target)
        record_row=dict(index=index,entry=entry,status='failed')
        result['invocations'].append(record_row); result.update(launched=index+1,unexecuted=65-index)
        write(output/'progress.json',result)
        process=launch(index,entry)
        samples=account(index,entry,process)
        require(len(samples)==entry['invocation']['observations'],'invocation sample count mismatch')
        integrity()
        record_row.update(status='passed',process=process,samples=samples)
        key='warmup_observations' if entry['invocation']['warmup'] else 'measured_observations'
        result[key]+=len(samples)
        write(output/'progress.json',result)
        print(index+1,'/66 passed',flush=True)
    require(result['measured_observations']==600 and result['warmup_observations']==6,'observation count mismatch')


def workload(entry,timeout=30):
    env,credentials=r.session(); target=Path(entry['argv'][-1])
    write(target.with_suffix('.command.json'),entry)
    process=o.gate.smoke.execute(entry['argv'],target,env,credentials,timeout=timeout)
    write(target.with_suffix('.process.json'),process)
    return process


def elevated(argv,output,name,timeout=600):
    # Elevation is limited to the frozen installer or the bounded recorder worker.
    return r.command(['sudo','-A',*argv],output,name,timeout=timeout)


def stage_worker(request,output):
    require(os.geteuid()==0,'staging requires scoped elevation')
    config=read(request); built=Path(config['built']); mode=config['mode']; variant=config['variant']
    require((mode,variant) in KEYS,'unknown staging configuration')
    o.check_output(built)
    require(read(built/'assessment.json')['status']=='built' and o.digest(built/'seal.json')==config['built_seal'],'staging build drift')
    require(output.absolute()==output.resolve() and output.parents[2]==Path('/run') and
            output.parent.name==mode and output.name==variant and output.parents[1].name.startswith('holonight-validation-'),
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


def recorder_worker(request,output):
    require(os.geteuid()==0,'recorder worker requires scoped elevation')
    require(output.is_dir() and output.absolute()==output.resolve(),'invalid recording directory')
    configuration=read(request)
    require(set(configuration)<= {'entry','clock'},'invalid recorder request')
    clock=configuration['clock']; entry=configuration.get('entry')
    data=output/'perf.data'
    require(data.is_file() and not data.is_symlink() and data.stat().st_uid==1000 and data.stat().st_size==0,
            'recorder requires a fresh desktop-owned evidence file')
    if entry:
        row=entry['invocation']
        require(row in v.schedule() and row['captured'],'unregistered recorder workload')
        require(entry['argv'][2]==str(o.old.FIXTURE_ROOT/'3200x2400.png') and
                entry['argv'][3:5]==['startup',str(row['observations'])],'recorder workload drift')
    def work(remaining):
        require(remaining>0,'recorder readiness exhausted session budget')
        return workload(entry,remaining) if entry else None
    bounds=dict(timeout_seconds=30,termination_grace_seconds=5,mmap_pages_per_cpu=256,
                all_cpus=True,clock='CLOCK_MONOTONIC',stack_sampling=False,fixture='3200x2400.png',
                variant=entry['invocation']['variant'] if entry else None,
                observations=entry['invocation']['observations'] if entry else 0,rehearsal=entry is None)
    # perf's offline readers require the file owner (or a root-owned file), even
    # when invoked by root. Keep the evidence desktop-owned and drop reader IDs.
    export_env,export_credentials=r.session()
    process,metadata=r.capture(output,work,bounds=bounds,export_env=export_env,export_credentials=export_credentials)
    metadata['clock']=clock
    write(output/'recording-metadata.json',metadata)
    if entry: write(output/'workload-process.json',process)


def normalize_recording(output,entry=None):
    require(os.geteuid()==1000,'scheduler analysis must run as desktop user')
    metadata=read(output/'recording-metadata.json')
    # Retain the original recording without broadening its permissions.
    identities=[]
    if entry:
        target=Path(entry['argv'][-1])
        for path in (target.with_suffix('.stderr'),target.with_suffix('.stdout')):
            for line in path.read_text().splitlines():
                if line.startswith(('VALIDATION ','TRACE ','DELIVERY ')):
                    identities.append(json.loads(line.split(' ',1)[1]))
    write(output/'task-identities.json',identities)
    normalized=r.n.normalize((output/'perf-export.stdout').read_text(),metadata,identities,str(output/'perf-export.stdout'))
    write(output/'scheduler.json',normalized)
    require(normalized['export_complete'] and not any(e['kind']=='loss' for e in normalized['events']),
            'recorder export incomplete or capture loss')


def execute(package,built,output):
    def run(result):
        require(os.geteuid()==1000,'orchestration must run as desktop user')
        check_package(package); o.check_output(built)
        require(read(built/'assessment.json')['status']=='built','native build blocked')
        require(read(built/'integrity.json')['before'][str(package)]==o.inventory(package),'native source provenance drift')
        marker=built.parent/(built.name+'-execution-started.json')
        with marker.open('x') as stream: json.dump(dict(output=str(output),built=str(built)),stream)
        targets=output/'observations'; targets.mkdir()
        protected=Path('/run')/('holonight-validation-'+output.name)
        require(not protected.exists() and not protected.is_symlink(),'protected runtime root reused')
        commands=planned_commands(built,protected,targets)
        installer=r.INSTALLER/'manage-images-generations.py'
        snapshots=read(Path(read(package/'provenance.json')['prepared'])/'input-integrity.json')['before']
        for name in ('manage-images-generations.py','install_state.py'):
            require(o.digest(r.INSTALLER/name)==snapshots[str(r.INSTALLER/name)],'frozen installer drift')
        stages=[]
        for mode,variant in KEYS:
            base=built/mode/variant
            stage=dict(mode=mode,variant=variant,source=str(base/'runtime'),destination=str(protected/mode/variant),
                argv=[sys.executable,'-B',str(Path(__file__).resolve()),'stage','--request',
                      str(output/('stage-'+mode+'-'+variant+'.json')),'--output',str(protected/mode/variant)])
            stage['elevated_argv']=['sudo','-A',*stage['argv']]
            if variant=='C':
                stage['installer_argv']=[sys.executable,'-B',str(installer),'install','--runtime',str(protected/mode/variant),
                    '--source',str(base/'runtime'),'--helper',str(base/'build/holonight-images/holonight-images-helper')]
            else: stage['copytree']=[str(base/'runtime'),str(protected/mode/variant)]
            stages.append(stage)
        # All commands, including elevated workers, are fixed before staging/rehearsal/workloads.
        clock=dict(name='CLOCK_MONOTONIC',provenance=dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                                                       host=Path('/etc/machine-id').read_text().strip()))
        recorder_commands=[]
        script=Path(__file__).resolve()
        for label in ('rehearsal',*[f'{i:03}' for i,e in enumerate(commands) if e['invocation']['captured']]):
            argv=[sys.executable,'-B',str(script),'record','--request',
                  str(output/(label+'-recorder-request.json')),'--output',str(output/('recording-'+label))]
            recorder_commands.append(dict(label=label,argv=argv,elevated_argv=['sudo','-A',*argv],
                                          perf_argv=r.record_argv(output/('recording-'+label)/'perf.data')))
        env,credentials=r.session()
        installer_hashes={str(r.INSTALLER/name):snapshots[str(r.INSTALLER/name)] for name in ('manage-images-generations.py','install_state.py')}
        write(output/'preregistration.json',dict(protocol=v.protocol(),commands=commands,staging=stages,recorders=recorder_commands,
              clock=clock,built=str(built),built_seal=o.digest(built/'seal.json'),package=str(package),
              fixture_hashes=read(package/'fixtures.json'),protected_runtime=str(protected),installer_sha256=o.digest(installer),
              installer_hashes=installer_hashes,host=list(os.uname()),environment=env,desktop_uid=1000))
        result.update(invocations=[],launched=0,unexecuted=66,measured_observations=0,warmup_observations=0)
        staged=[]
        def isolated(target): r.isolated(target)
        def integrity():
            o.check_output(built); check_package(package)
            for name,digest in read(package/'fixtures.json').items(): require(o.digest(Path(name))==digest,'fixture drift')
            for name,digest in installer_hashes.items(): require(o.digest(Path(name))==digest,'installer/support drift')
            require(clock['provenance']['boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'boot drift')
            for base,destination,variant,expected in staged:
                o.staged(base,destination,variant)
                require(o.gate.protected_inventory(destination/variant)==expected,'staged runtime drift')
        try:
            isolated(targets/'initial.json')
            for stage in stages:
                mode,variant=stage['mode'],stage['variant']
                write(output/('stage-'+mode+'-'+variant+'.json'),dict(mode=mode,variant=variant,built=str(built),
                    built_seal=o.digest(built/'seal.json'),execution=str(output),installer=str(installer),installer_sha256=o.digest(installer),
                    installer_hashes=installer_hashes))
                elevated(stage['argv'],output,'stage-'+mode+'-'+variant)
                destination=protected/mode
                inv=o.staged(built/mode,destination,variant)
                staged.append((built/mode,destination,variant,inv))
            def record(label,entry=None):
                path=output/('recording-'+label); path.mkdir()
                # perf opens the existing empty file. Its desktop ownership and
                # private read permissions survive the privileged recorder write.
                (path/'perf.data').touch(mode=0o600,exist_ok=False)
                write(output/(label+'-recorder-request.json'),dict(entry=entry,clock=clock))
                command=next(c['argv'] for c in recorder_commands if c['label']==label)
                elevated(command,output,'recorder-'+label,timeout=100)
                normalize_recording(path,entry)
                return read(path/'workload-process.json') if entry else None
            integrity(); record('rehearsal'); integrity()
            reporter=module('run_validation_report','report-preview-validation.py')
            def launch(index,entry):
                return record(f'{index:03}',entry) if entry['invocation']['captured'] else workload(entry)
            def account(index,entry,process):
                target=Path(entry['argv'][-1])
                samples=o.validate(target,dict(entry['invocation'],mode='v4'),process,1000)
                after=o.gate.scope_snapshot(1000,env,credentials)
                write(target.with_suffix('.scopes-after.json'),after); require(after['isolated'],'post-workload scope isolation failed')
                reporter.invocation(entry,index,built,output)
                return samples
            run_schedule(commands,output,result,integrity,isolated,launch,account)
            result['status']='complete'
        finally:
            checks={}
            for name,check in [('integrity',integrity),('scopes',lambda:isolated(targets/'final.json')),
                               ('residuals',lambda:r.residuals(output))]:
                try: check(); checks[name]=dict(passed=True)
                except ERRORS as error: checks[name]=dict(passed=False,failure=str(error))
            write(output/'execution-final-checks.json',checks)
            if not all(c['passed'] for c in checks.values()): result['status']='blocked'
    return action(output,[package,built],run)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('build','execute','record','stage'))
    for name in ('prepared','built','request'): parser.add_argument('--'+name,type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.action=='stage':
        stage_worker(args.request,args.output); sys.exit(0)
    if args.action=='record':
        recorder_worker(args.request,args.output); sys.exit(0)
    require(args.prepared is not None,'--prepared required')
    result=build(args.prepared,args.output) if args.action=='build' else execute(args.prepared,args.built,args.output)
    print(result); sys.exit(result['status'] not in ('built','complete'))
