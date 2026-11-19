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
inputs = c.historical.e.load('independent_native_inputs', Path(__file__).parent/'inputs.py')


DETECTOR = r"""
static bool adaptiveNonuniform(const QImage& image, const std::atomic_bool& cancelled) {
  switch (image.format()) {
    case QImage::Format_RGB32:
    case QImage::Format_ARGB32:
    case QImage::Format_ARGB32_Premultiplied:
    case QImage::Format_RGBX8888:
    case QImage::Format_RGBA8888:
    case QImage::Format_RGBA8888_Premultiplied: break;
    default: return false;
  }
  if (image.width() < 2 || image.height() < 2) return false;
  const int nx = std::min(32, image.width()-1), ny = std::min(32, image.height()-1);
  int complex = 0;
  for (int j=0; j<ny; ++j) {
    if (cancelled.load()) return false;
    int y = 1 + ((2*j+1)*(image.height()-1))/(2*ny);
    const auto* row = reinterpret_cast<const quint32*>(image.constScanLine(y));
    const auto* upper = reinterpret_cast<const quint32*>(image.constScanLine(y-1));
    for (int i=0; i<nx; ++i) {
      int x = 1 + ((2*i+1)*(image.width()-1))/(2*nx);
      complex += row[x] != row[x-1] && row[x] != upper[x];
    }
  }
  return 4*complex >= nx*ny;
}
"""
ANCHOR = '  if (cancelled.load() || !tagged.save(&file, "PNG")) {'
WRITER = '''  const bool compress = request.kind == Kind::Raster && adaptiveNonuniform(image, cancelled);
  QImageWriter writer(&file, "PNG");
  if (compress) writer.setCompression(11);
  if (cancelled.load() || !(compress ? writer.write(tagged) : tagged.save(&file, "PNG"))) {'''


def summarize(raw):
    ids=[f'{name}-{tier}' for name in ('textured','flat','alpha','oriented','two-color','gradient','panel') for tier in (128,256,512,1024)]
    h.require(raw['qt']=='6.12.0' and [r['id'] for r in raw['corpus']]==ids,'corpus')
    cursor=0
    cells={}
    for image in raw['corpus']:
        identity=image['id']
        expected=[(m,True,-1,0) for m in ('default','adaptive')]
        for block in range(6):
            for offset in range(2):
                expected += [(('default','adaptive')[(block+offset)%2],False,block,n) for n in range(5)]
        rows=raw['rows'][cursor:cursor+62]
        cursor+=62
        h.require(len(rows)==62,'incomplete stores')
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
        for mode in ('default','adaptive'):
            group=[r for r in rows if r['mode']==mode]
            h.require(all(r['metadata']==texts and r['bytes']==group[0]['bytes'] and r['sha256']==group[0]['sha256'] for r in group),'encoding drift')
            times=sorted(r['ns'] for r in group if not r['warmup'])
            h.require(len(times)==30,'sample count')
            cells[identity][mode]=dict(bytes=group[0]['bytes'],median=statistics.median(times),p95=times[28])
    h.require(cursor==len(raw['rows']),'extra stores')
    eligible=[]
    reasons={}
    for mode in ('adaptive',):
        failures=[i for i in ids if cells[i][mode]['bytes']*4>cells[i]['default']['bytes']*5]
        primary=cells['textured-256']
        faster=primary[mode]['median']<primary['default']['median'] and primary[mode]['p95']<primary['default']['p95']
        reasons[mode]=dict(size_failures=failures,primary_faster=faster)
        if not failures and faster:
            eligible.append(mode)

    return dict(cells=cells,eligibility=reasons,selected=eligible[0] if eligible else None,decision='Evidence insufficient' if eligible else 'Deferred')


def verify(root):
    h.require(root == c.OUTPUT,'fixed evidence root')
    inventory=h.sealed(root)
    h.require(h.read(root/'binding.json')==c.prerequisite(),'provenance')
    captured_tools=h.read(root/'tools.json')
    for name,digest in captured_tools.items():
        h.require(h.digest(root/'tools'/c.historical.snapshot_name(name))==digest,'tool snapshot')
    frozen=h.read(root/'freeze.json')
    h.require(all(inventory.get(name)==digest for name,digest in frozen.items()),'frozen inputs changed')
    assessment=h.read(root/'assessment.json')
    # Phase membership is frozen; later tooling may grow without invalidating this phase.
    h.require(all(h.digest(Path(name)) == digest for name,digest in captured_tools.items()), 'captured tool drift')
    h.require(h.digest(root/'qpnghandler.cpp')==c.SOURCE_SHA,'Qt source hash')
    source=(root/'qpnghandler.cpp').read_text()
    h.require('compression = (compression * 9) / 91;' in source and 'png_set_compression_level(png_ptr, compression);' in source,'Qt mapping source')
    h.require((root/'3.stderr').read_text().splitlines()==['PNG_LEVEL 1','PNG_LEVEL 0'],'live mapping')
    before=c.historical.Q/'C/source/holonight-thumbnails'
    original=(before/'src/cache.cpp').read_text()
    for mode in ('default','adaptive'):
        actual=(root/'sources'/mode/'src/cache.cpp').read_text()
        if mode!='default':
            actual=actual.replace('#include <QSaveFile>\n#include <QImageWriter>\n'+DETECTOR,'#include <QSaveFile>').replace(WRITER, '  if (cancelled.load() || !tagged.save(&file, "PNG")) {')
        h.require(actual==original,'store source allowlist')
        for name,digest in h.inventory(before).items():
            if name!='src/cache.cpp':
                h.require(h.digest(root/'sources'/mode/name)==digest,'unrelated source mutation')
        if mode!='default':
            header=(before/'include/holonight_thumbnails/cache.h').read_text()
            h.require((root/'sources'/mode/'store.h').read_text()==header.replace('HolonightThumbnails','Store_'+mode),'renamed header drift')
    h.require(h.inventory(root/'native')==dict({Path(name).name: digest for name,digest in captured_tools.items() if Path(name).parent == c.DIRECTORY/'native'}, **{'detector.h': hashlib.sha256(DETECTOR.encode()).hexdigest(), 'detector-test.h': hashlib.sha256(DETECTOR.replace('std::atomic_bool', 'ScanCancellation').encode()).hexdigest()}),'native harness drift')
    # Reconstruct exact command and environment contracts without importing run.py.
    prefix=c.historical.BUILT/'common/prefix'
    expected=[['cmake','-S',str(root/'native'),'-B',str(root/'native-build'),'-G','Ninja','-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix)],
        ['cmake','--build',str(root/'native-build'),'--parallel','4'],['ldd',str(root/'native-build/investigate')],
        [str(root/'native-build/investigate'),'mapping'],[str(root/'native-build/investigate'),'materialize',str(root/'corpus'),str(root/'raw.json')],
        [str(root/'native-build/investigate'),'measure',str(root/'corpus'),str(root/'raw.json'),'<validated-manifest-sha256>']]
    h.require(h.read(root/'schedule.json')==expected,'command schedule')
    env=dict(PATH='/usr/bin:/bin',HOME=str(root/'home'),LANG='C.UTF-8',QT_QPA_PLATFORM='offscreen',XDG_CACHE_HOME=str(root/'cache'))
    h.require(h.read(root/'environment.json')==env,'environment')
    limits=(600,600,30,30,300,300)
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
        launch=h.read(root/f'command-{index}.json')
        if index == 5:
            argv=argv[:-1]+[h.read(root/'inputs-validated.json')['manifest_sha256']]
        timeout=launch['timeout_seconds']
        h.require(type(timeout) in (int,float) and 0 < timeout <= limits[index], 'command deadline')
        if index < 4:
            h.require(timeout == limits[index], 'fixed command timeout')
        h.require(launch==dict(argv=argv,cwd=str(root/'corpus'),environment=effective,timeout_seconds=timeout,start_new_session=True),'command contract')
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
    h.require(attempted==successful==6,'incomplete investigation commands')
    raw=h.read(root/'raw.json')
    validated=inputs.validate(root/'corpus')
    h.require(h.read(root/'inputs-validated.json') == validated, 'controller input validation')
    input_seal=h.read(root/'inputs-seal.json')
    h.require(all(h.digest(root/'corpus'/name)==digest for name,digest in input_seal.items()), 'sealed pre-store inputs')
    h.require(h.read(root/'aggregate-result.json')['stop_ns']-h.read(root/'aggregate.json')['start_ns'] <= 300*10**9, 'aggregate deadline')
    h.require(h.read(root/'result-4.json')['start_ns'] >= h.read(root/'aggregate.json')['start_ns'] and h.read(root/'result-5.json')['stop_ns'] <= h.read(root/'aggregate-result.json')['stop_ns'], 'aggregate command binding')
    h.require(h.read(root/'result-5.json')['stop_ns']-h.read(root/'aggregate.json')['start_ns'] <= 300*10**9, 'shared execution deadline')
    h.require(h.read(root/'corpus/inputs.json') == raw['corpus'], 'pre-store corpus binding')
    summary=summarize(raw)
    assessment=h.read(root/'assessment.json')
    h.require(assessment==dict(status='complete',completed=6,failure=None,**summary),'assessment reconstruction')
    # Independent PNG decoding checks actual retained bytes, pixels, alpha and metadata.
    for image in raw['corpus']:
        frozen=root/'corpus'/(image['id']+'-input.rgba')
        h.require(h.digest(frozen)==image['pixels'] and frozen.stat().st_size==image['width']*image['height']*4,'materialized thumbnail')
        if image['writer'] == 'default':
            h.require((root/'corpus'/(image['id']+'-default.png')).read_bytes() == (root/'corpus'/(image['id']+'-adaptive.png')).read_bytes(), 'default-selected byte equality')
        for mode in ('default','adaptive'):
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
        *(root/'native-build'/('libstore_'+mode+'.a') for mode in ('default','adaptive'))]
    h.require(artifacts=={str(p):h.digest(p) for p in paths},'compiled artifact identities')
    return dict(status='passed',decision=summary['decision'],selected=summary['selected'],stores=len(raw['rows']),
        measured_stores=1680,cleanup=True,imports_runner=False,evidence_seal=h.digest(root/'seal.json'),verifier_sha256=h.digest(Path(__file__)))


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
