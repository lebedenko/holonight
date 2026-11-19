#!/usr/bin/env python3
"""Independent, process-free reconstruction of encoding evidence. No controllers imported."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from PIL import Image

sys.dont_write_bytecode = True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import contract as c
sys.path.pop(0)
h = c.h


def summarize(raw):
    ids=[f'{name}-{tier}' for name in ('textured','flat','alpha','oriented') for tier in (128,256,512,1024)]
    h.require(raw['qt']=='6.12.0' and [r['id'] for r in raw['corpus']]==ids,'corpus')
    cursor=0
    cells={}
    for image in raw['corpus']:
        identity=image['id']
        expected=[(m,True,-1,0) for m in ('default','11','0')]
        for block in range(6):
            for offset in range(3):
                expected += [(('default','11','0')[(block+offset)%3],False,block,n) for n in range(5)]
        rows=raw['rows'][cursor:cursor+93]
        cursor+=93
        h.require(len(rows)==93,'incomplete stores')
        for row, coordinates in zip(rows,expected):
            h.require(row['id']==identity and (row['mode'],row['warmup'],row['block'],row['observation'])==coordinates and type(row['warmup']) is bool,'schedule')
            h.require(type(row['ns']) is int and row['ns']>0 and type(row['bytes']) is int and row['bytes']>0,'malformed timing/size')
            h.require(all(row[k]==image[k] for k in ('pixels','alpha','icc')),'round trip')
        cells[identity]={}
        texts=rows[0]['metadata']
        h.require(texts.get('Thumb::MTime')=='1700000000' and texts.get('Thumb::Size')=='1234567' and
            texts.get('X-HoloNight::MTimeMsec')=='1700000000123' and texts.get('Files::Revision')=='encoding-trial-v1' and
            texts.get('Files::OrientationPolicy')==texts.get('X-HoloNight::OrientationPolicy')=='applied-v1' and
            texts.get('Thumb::URI','').endswith('/source-'+identity.rsplit('-',1)[0]),'required metadata')
        for mode in ('default','11','0'):
            group=[r for r in rows if r['mode']==mode]
            h.require(all(r['metadata']==texts and r['bytes']==group[0]['bytes'] and r['sha256']==group[0]['sha256'] for r in group),'encoding drift')
            times=sorted(r['ns'] for r in group if not r['warmup'])
            h.require(len(times)==30,'sample count')
            cells[identity][mode]=dict(bytes=group[0]['bytes'],median=statistics.median(times),p95=times[28])
    h.require(cursor==len(raw['rows']),'extra stores')
    eligible=[]
    reasons={}
    for mode in ('11','0'):
        failures=[i for i in ids if cells[i][mode]['bytes']*4>cells[i]['default']['bytes']*5]
        primary=cells['textured-256']
        faster=primary[mode]['median']<primary['default']['median'] and primary[mode]['p95']<primary['default']['p95']
        reasons[mode]=dict(size_failures=failures,primary_faster=faster)
        if not failures and faster:
            eligible.append(mode)
    eligible.sort(key=lambda mode:(cells['textured-256'][mode]['p95'],cells['textured-256'][mode]['median'],sum(cells[i][mode]['bytes'] for i in ids),mode!='11'))
    return dict(cells=cells,eligibility=reasons,selected=eligible[0] if eligible else None,decision='Evidence insufficient' if eligible else 'Deferred')


def verify(root):
    h.require(root in (c.OUTPUT,c.STOPPED_OUTPUT),'fixed evidence root')
    inventory=h.sealed(root)
    h.require(h.read(root/'binding.json')==c.prerequisite(),'provenance')
    captured_tools=h.read(root/'tools.json')
    for name,digest in captured_tools.items():
        h.require(h.digest(root/'tools'/c.historical.snapshot_name(name))==digest,'tool snapshot')
    frozen=h.read(root/'freeze.json')
    h.require(all(inventory.get(name)==digest for name,digest in frozen.items()),'frozen inputs changed')
    assessment=h.read(root/'assessment.json')
    if root==c.STOPPED_OUTPUT:
        return verify_stopped(root,assessment,captured_tools)
    h.require(captured_tools==c.tools(),'tool identities')
    h.require(h.digest(root/'qpnghandler.cpp')==c.SOURCE_SHA,'Qt source hash')
    source=(root/'qpnghandler.cpp').read_text()
    h.require('compression = (compression * 9) / 91;' in source and 'png_set_compression_level(png_ptr, compression);' in source,'Qt mapping source')
    h.require((root/'3.stderr').read_text().splitlines()==['PNG_LEVEL 1','PNG_LEVEL 0'],'live mapping')
    before=c.historical.Q/'C/source/holonight-thumbnails'
    original=(before/'src/cache.cpp').read_text()
    for mode in ('default','11','0'):
        actual=(root/'sources'/mode/'src/cache.cpp').read_text()
        if mode!='default':
            actual=actual.replace('#include <QSaveFile>\n#include <QImageWriter>','#include <QSaveFile>').replace(
                '  QImageWriter writer(&file, "PNG");\n  writer.setCompression('+mode+');\n  if (cancelled.load() || !writer.write(tagged)) {',
                '  if (cancelled.load() || !tagged.save(&file, "PNG")) {')
        h.require(actual==original,'store source allowlist')
        for name,digest in h.inventory(before).items():
            if name!='src/cache.cpp':
                h.require(h.digest(root/'sources'/mode/name)==digest,'unrelated source mutation')
        if mode!='default':
            header=(before/'include/holonight_thumbnails/cache.h').read_text()
            h.require((root/'sources'/mode/'store.h').read_text()==header.replace('HolonightThumbnails','Store_'+mode),'renamed header drift')
    h.require(h.inventory(root/'native')==h.inventory(c.DIRECTORY/'native'),'native harness drift')
    # Reconstruct exact command and environment contracts without importing run.py.
    prefix=c.historical.BUILT/'common/prefix'
    expected=[['cmake','-S',str(root/'native'),'-B',str(root/'native-build'),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix)],
        ['cmake','--build',str(root/'native-build'),'--parallel','4'],['ldd',str(root/'native-build/investigate')],
        [str(root/'native-build/investigate'),'mapping'],[str(root/'native-build/investigate'),str(root/'corpus'),str(root/'raw.json')]]
    h.require(h.read(root/'schedule.json')==expected,'command schedule')
    env=dict(PATH='/usr/bin:/bin',HOME=str(root/'home'),LANG='C.UTF-8',QT_QPA_PLATFORM='offscreen',XDG_CACHE_HOME=str(root/'cache'))
    h.require(h.read(root/'environment.json')==env,'environment')
    limits=(600,600,30,30,300)
    h.require(h.read(root/'limits.json')==dict(command_seconds=list(limits),shared_cleanup_seconds=5),'registered time bounds')
    previous=0
    successful=0
    attempted=0
    for index,argv in enumerate(expected):
        if not (root/f'command-{index}.json').exists():
            break
        attempted+=1
        effective=dict(env)
        if index==3:
            effective['LD_PRELOAD']=str(root/'native-build/libmapping.so')
        h.require(h.read(root/f'command-{index}.json')==dict(argv=argv,cwd=str(root/'corpus'),environment=effective,timeout_seconds=limits[index],start_new_session=True),'command contract')
        result=h.read(root/f'result-{index}.json')
        okay=verify_result(result,previous)
        previous=result['stop_ns']
        if not okay:
            break
        successful+=1
    h.require({p.name for p in root.glob('command-*.json')}=={f'command-{i}.json' for i in range(attempted)} and
        {p.name for p in root.glob('result-*.json')}=={f'result-{i}.json' for i in range(attempted)},'continued execution after failure or missing result')
    h.require(assessment['completed']==successful,'completed command accounting')
    if assessment['status']=='stopped':
        h.require(assessment['decision']=='Evidence insufficient' and assessment['failure'],'unexplained stopped execution')
        return dict(status='passed',outcome='stopped',decision='Evidence insufficient',selected=None,
            cleanup=all(h.read(root/f'result-{i}.json')['cleanup'] for i in range(attempted)),
            completed=successful,attempted=attempted,imports_runner=False,
            evidence_seal=h.digest(root/'seal.json'),verifier_sha256=h.digest(Path(__file__)))
    h.require(attempted==successful==5,'incomplete investigation commands')
    raw=h.read(root/'raw.json')
    summary=summarize(raw)
    assessment=h.read(root/'assessment.json')
    h.require(assessment==dict(status='complete',completed=5,failure=None,**summary),'assessment reconstruction')
    # Independent PNG decoding checks actual retained bytes, pixels, alpha and metadata.
    for image in raw['corpus']:
        for mode in ('default','11','0'):
            row=next(r for r in raw['rows'] if r['id']==image['id'] and r['mode']==mode)
            path=root/'corpus'/(image['id']+'-'+mode+'.png')
            h.require(path.stat().st_size==row['bytes'] and h.digest(path)==row['sha256'],'encoded bytes')
            with Image.open(path) as decoded:
                h.require(decoded.size==(image['width'],image['height']),'dimensions')
                h.require(hashlib.sha256(decoded.convert('RGBA').tobytes()).hexdigest()==image['pixels'],'independent pixel decode')
                h.require(('A' in decoded.getbands())==image['alpha'],'independent alpha')
                h.require(all(decoded.text.get(k)==v for k,v in row['metadata'].items()),'independent metadata')
                if decoded.info.get('icc_profile'):
                    h.require(hashlib.sha256(decoded.info['icc_profile']).hexdigest()==image['icc'],'independent ICC')
    # Bind every dynamic library resolved by the exact built executable.
    libraries=h.read(root/'libraries.json')
    h.require(libraries and all(h.digest(Path(p))==digest for p,digest in libraries.items()),'runtime identities')
    h.require(any('libQt6Gui' in p for p in libraries) and any('libpng' in p for p in libraries),'PNG runtime identity')
    artifacts=h.read(root/'artifacts.json')
    paths=[root/'native-build/investigate',root/'native-build/libmapping.so',
        *(root/'native-build'/('libstore_'+mode+'.a') for mode in ('default','11','0'))]
    h.require(artifacts=={str(p):h.digest(p) for p in paths},'compiled artifact identities')
    return dict(status='passed',decision=summary['decision'],selected=summary['selected'],stores=len(raw['rows']),
        measured_stores=1440,cleanup=True,imports_runner=False,evidence_seal=h.digest(root/'seal.json'),verifier_sha256=h.digest(Path(__file__)))


def verify_result(result,previous):
    h.require(type(result['start_ns']) is int and type(result['stop_ns']) is int and
        previous<=result['start_ns']<=result['stop_ns'],'command chronology')
    h.require(all(type(result[k]) is bool for k in ('timed_out','cleanup','reaped','group_absent')),'malformed command flags')
    h.require(type(result['cleanup_seconds']) in (int,float) and math.isfinite(result['cleanup_seconds']) and
        result['cleanup_seconds']>=0,'invalid cleanup duration')
    if result['pid'] is not None:
        h.require(type(result['pid']) is int and result['pid']>0,'invalid owned PID')
    if result['exit'] is not None:
        h.require(type(result['exit']) is int,'malformed exit status')
    if result['cleanup']:
        h.require(result['cleanup_seconds']<=5 and result['cleanup_failure'] is None and result['group_absent'] and
            (result['pid'] is None or (result['reaped'] and result['exit'] is not None)),'cleanup proof')
    else:
        h.require(bool(result['cleanup_failure']),'unexplained cleanup failure')
    if result['timed_out']:
        h.require(bool(result['failure']),'unexplained timeout')
    okay=result['failure'] is None and result['cleanup']
    if okay:
        h.require(result['pid'] is not None and result['exit']==0 and result['reaped'] and not result['timed_out'],'failed command marked successful')
    return okay


def verify_stopped(root,assessment,captured_tools):
    """A stopped attempt can establish insufficiency, never eligibility or cleanup."""
    # This is an audit of one retained interrupted attempt, not acceptance of arbitrary
    # resealed partial files. A new attempt needs its own registered contract.
    h.require(h.digest(root/'seal.json')=='f7375f273dcc0d899fad9ca9ca78dd66525844a208a9a9967da10b9fabd1d58e',
        'retained stopped evidence identity changed')
    h.require(assessment['decision']=='Evidence insufficient' and assessment['completed']==4 and
        'timed out after 30 seconds' in assessment['failure'],'stopped investigation accounting')
    h.require(not (root/'raw.json').exists(),'unexpected complete raw evidence')
    h.require(not (root/'result-4.json').exists(),'unexpected successful investigation result')
    expected=h.read(root/'schedule.json')
    h.require(len(expected)==5,'stopped schedule size')
    previous=0
    for index in range(4):
        command=h.read(root/f'command-{index}.json')
        h.require(command['argv']==expected[index] and command['cwd']==str(root/'corpus'),'stopped command binding')
        result=h.read(root/f'result-{index}.json')
        h.require(result['exit']==0 and result['cleanup'] is True and previous<=result['start_ns']<=result['stop_ns'],'completed command evidence')
        previous=result['stop_ns']
    command=h.read(root/'command-4.json')
    h.require(command['argv']==[str(root/'native-build/investigate'),str(root/'corpus'),str(root/'raw.json')] and
        command['timeout_seconds']==30 and 'LD_PRELOAD' not in command['environment'],'stopped workload contract')
    h.require((root/'3.stderr').read_text().splitlines()==['PNG_LEVEL 1','PNG_LEVEL 0'],'live compression mapping')
    h.require(h.digest(root/'qpnghandler.cpp')==c.SOURCE_SHA,'matching Qt source')
    libraries=h.read(root/'libraries.json')
    h.require(libraries and all(h.digest(Path(p))==digest for p,digest in libraries.items()),'stopped runtime identities')
    controller=str(c.DIRECTORY/'run.py')
    h.require(controller in captured_tools,'captured controller missing')
    captured=(root/'tools'/c.historical.snapshot_name(controller)).read_text()
    h.require('cleanup.terminate(process,deadline=cleanup_start+5)' in captured and
        'os.killpg(process.pid,0)' in captured,'owned cleanup implementation missing')
    return dict(status='passed',outcome='stopped',decision='Evidence insufficient',selected=None,
        complete_raw_observations=False,cleanup='unverified: timeout result was not persisted',
        imports_runner=False,evidence_seal=h.digest(root/'seal.json'),verifier_sha256=h.digest(Path(__file__)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    h.require(not args.output.exists() and not args.output.is_relative_to(args.evidence),'verification destination collision')
    try:
        result=verify(args.evidence)
    except (OSError,ValueError,KeyError,TypeError,IndexError) as error:
        result=dict(status='failed',decision='Evidence insufficient',failure=str(error))
    h.write(args.output,result)
    print(json.dumps(result,indent=2))
    sys.exit(result['status']!='passed')
