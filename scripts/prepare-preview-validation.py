#!/usr/bin/env python3
"""Prepare private A/C validation probes from sealed v4 sources; no subprocesses."""
import argparse
import difflib
import importlib.util
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validation_predecode', Path(__file__).with_name('report-preview-predecode.py'))
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
o, require, read, write = p.o, p.require, p.read, p.write
DEFAULT = ROOT/'build/preview-predecode-20261115-06'
GROUPS = ('source', 'harness-source')
ERRORS = (OSError, ValueError, KeyError, TypeError, IndexError)
COMBINATIONS = [('A','baseline'), ('C','baseline'), ('A','validation'), ('C','validation'), ('A','captured'), ('C','captured')]
HEADER = r'''
// Private validation stream. Independent identities never advance v3/v4 sequences.
namespace ValidationTrace {
inline std::atomic<unsigned long long> sequence{1};
inline thread_local unsigned long long parent=0, validation=0;
struct Scope {
  const char* operation;
  unsigned long long span=sequence.fetch_add(1), previous=parent, previousValidation=validation;
  long ordinal;
  StandbyTrace::Context context=StandbyTrace::current;
  int exceptions=std::uncaught_exceptions();
  bool active=true;
  void event(const char* edge, const char* outcome) const {
    char line[2048];
    int n=std::snprintf(line,sizeof(line),"VALIDATION {\"version\":1,\"ns\":%lld,\"pid\":%d,\"tid\":%ld,\"service\":%s,\"observation\":%s,\"job\":%s,\"worker\":%s,\"preparation\":%s,\"validation\":%llu,\"span\":%llu,\"parent\":%llu,\"ordinal\":%ld,\"operation\":\"%s\",\"edge\":\"%s\",\"outcome\":\"%s\"}\n",
      DeliveryTrace::now(),getpid(),syscall(SYS_gettid),DeliveryTrace::id(context.service).c_str(),DeliveryTrace::id(context.observation).c_str(),DeliveryTrace::id(context.job).c_str(),DeliveryTrace::id(context.worker).c_str(),DeliveryTrace::id(context.preparation).c_str(),validation,span,previous,ordinal,operation,edge,outcome);
    if(n>0 && n<static_cast<int>(sizeof(line))) { auto ignored=write(2,line,n); (void)ignored; }
  }
  explicit Scope(const char* op,long file=-1,bool root=false):operation(op),ordinal(file) {
    if(root) validation=span;
    event("begin","unavailable"); parent=span;
  }
  void finish() {
    if(!active) return;
    event("end",std::uncaught_exceptions()>exceptions ? "exception" : "returned");
    parent=previous; validation=previousValidation; active=false;
  }
  ~Scope() { finish(); }
  Scope(const Scope&)=delete;
  Scope& operator=(const Scope&)=delete;
};
template<class F> auto measure(const char* name,long ordinal,F operation) {
  Scope scope(name,ordinal);
  return operation();
}
}
'''


def schedule():
    rows = []
    def append(combinations, block, count):
        for variant, arm in combinations:
            rows.append(dict(variant=variant, arm=arm, mode='baseline' if arm=='baseline' else 'validation',
                             captured=arm=='captured', block=block, warmup=block is None,
                             observations=count, fixture='3200x2400.png'))
    append(COMBINATIONS, None, 1)
    for block in range(10):
        offset = block % 6
        order = COMBINATIONS[offset:] + COMBINATIONS[:offset]
        append(list(reversed(order)) if block % 2 else order, block, 10)
    return rows


def protocol():
    return dict(schedule=schedule(), invocations=66, measured_observations=600, endpoint_mappings=1200,
                warmup_observations=6, jobs=4, timeout_seconds=30, termination_grace_seconds=5,
                retries=0, cache_flushing=False, affinity_changes=False, artificial_load=False,
                recorder=dict(all_cpus=True, clock='CLOCK_MONOTONIC', mmap_pages_per_cpu=256,
                              stack_sampling=False, events=['sched_switch','sched_wakeup','sched_wakeup_new',
                              'sched_process_fork','sched_process_exec','sched_process_exit']),
                interpretation='Diagnostic only; no overhead subtraction, significance or qualification threshold. '
                'Combined file reading/hashing does not isolate hashing CPU cost. Non-runnable time identifies no cause.')


def replace(text, old, new, anchors, file):
    require(old and text.count(old)==1, 'missing/duplicate literal anchor: '+file+': '+old[:100])
    anchors.append(dict(file=file, anchor=old, replacement=new))
    return text.replace(old,new,1)


def instrument(text, name):
    anchors = []
    def edit(old,new):
        nonlocal text
        text=replace(text,old,new,anchors,name)
    def scope(anchor, declaration):
        edit(anchor, anchor+'\n'+declaration)
    def boundary(anchor, before):
        edit(anchor,before+'\n'+anchor)
    if name.endswith('/verification.cpp'):
        scope('  StandbyTrace::Scope trace("runtime_validation", &root, -1);',
              '  ValidationTrace::Scope validation_root("runtime", -1, true);\n  ValidationTrace::Scope initial("initial_path_manifest");')
        edit('  const auto manifest = parseControl(fileBytes(root + "/manifest.json"));',
             '  initial.finish();\n  const auto manifest = ValidationTrace::measure("manifest_parse", -1, [&] {\n'
             '    return parseControl(ValidationTrace::measure("manifest_read", -1, [&] { return fileBytes(root + "/manifest.json"); }));\n  });\n'
             '  ValidationTrace::Scope policy("manifest_policy");')
        boundary('  for (auto value : manifest["files"].toArray()) {', '  policy.finish();\n  long validation_ordinal = 0;')
        scope('  for (auto value : manifest["files"].toArray()) {',
              '    const auto ordinal = validation_ordinal++;\n    ValidationTrace::Scope file_scope("file", ordinal);\n'
              '    ValidationTrace::Scope record_scope("record_prepare", ordinal);')
        scope('    const auto absolute = root + "/" + path;', '    record_scope.finish();\n    ValidationTrace::Scope attributes("attributes", ordinal);')
        boundary('    QFile file(absolute);', '    attributes.finish();')
        for operation, expression in [('file_open','file.open(QIODevice::ReadOnly)'),
                                      ('read_hash','hash.addData(&file)'),
                                      ('digest_compare','QString::fromLatin1(hash.result().toHex()) != record["sha256"].toString()')]:
            # file.open also occurs in fileBytes; match the original hash condition literally.
            if operation=='file_open':
                edit('    if (!file.open(QIODevice::ReadOnly) || !hash.addData(&file) ||',
                     '    if (!ValidationTrace::measure("file_open", ordinal, [&] { return file.open(QIODevice::ReadOnly); }) || !hash.addData(&file) ||')
            else:
                edit(expression,'ValidationTrace::measure("'+operation+'", ordinal, [&] { return '+expression+'; })')
        boundary('  for (const auto* required :', '  ValidationTrace::Scope required_scope("required_files");')
        scope('      throw ProtocolError("runtime inventory incomplete");\n    }\n  }',
              '  required_scope.finish();\n  ValidationTrace::Scope inventory_scope("inventory");')
    elif name.endswith('/generation.cpp'):
        scope('  StandbyTrace::Scope trace("generation_validation", this, -1);',
              '  ValidationTrace::Scope validation_root("generation", -1, true);')
        boundary('    Isolation::verifyProtectedRuntime(state_->directory);',
                 '    ValidationTrace::Scope protected_base("protected_base");')
        scope('    Isolation::verifyProtectedRuntime(state_->directory);',
              '    protected_base.finish();\n    ValidationTrace::Scope selection("selector_descriptors");')
        boundary('    Isolation::verifyProtectedRuntime(directory);',
                 '    selection.finish();\n    ValidationTrace::Scope protected_generation("protected_generation");')
        scope('    Isolation::verifyProtectedRuntime(directory);', '    protected_generation.finish();')
        edit('    auto binds = Isolation::verifyRuntime(directory);',
             '    auto binds = ValidationTrace::measure("nested_runtime", -1, [&] { return Isolation::verifyRuntime(directory); });\n'
             '    ValidationTrace::Scope manifest_scope("generation_manifest_open_read");')
        scope('    const auto manifestBytes = manifest.readAll();',
              '    manifest_scope.finish();\n    ValidationTrace::Scope parse_scope("generation_manifest_parse_policy");')
        boundary('    const auto digest =', '    parse_scope.finish();\n    ValidationTrace::Scope digest_scope("generation_manifest_digest");')
        boundary('    struct stat afterSelector{};', '    digest_scope.finish();\n    ValidationTrace::Scope final_scope("generation_final_identity");')
        boundary('    GenerationLease lease;', '    final_scope.finish();')
    else:
        raise ValueError('unsupported probe file: '+name)
    return text,anchors


def verify_seal(root, exact=True):
    require(root.absolute()==root.resolve(), 'symlink input ancestor')
    if exact:
        o.check_output(root)
        return o.inventory(root)
    # Historical preparation seals predate appended execution/report directories.
    # Validate every originally sealed file, without treating later evidence as edits.
    expected=read(root/'seal.json')
    for name,digest in expected.items():
        path=o.prep.child(root,name)
        require(o.digest(path)==digest, 'historical sealed file drift: '+str(path))
    return expected


def provenance(evidence, output, consume):
    """Resolve only recorded frozen inputs; do not execute historical recipes."""
    verify_seal(evidence)
    require(consume(evidence/'assessment.json')['status']=='complete', 'predecode evidence blocked')
    integrity=consume(evidence/'integrity.json')
    require(integrity['passed'], 'predecode integrity blocked')
    # Bind preparation and qualification to the completed source comparison.
    chain=consume(evidence/'source-comparison.json')['chain']
    prepared=Path(chain[0]).parents[2]
    qualification=Path(chain[-1]).parents[1]
    require(chain[0]==str(prepared/'v4/A/source') and chain[-1]==str(qualification/'A/source'), 'source provenance mismatch')
    verify_seal(prepared)
    manifest=consume(prepared/'manifest.json')
    require(manifest['status']=='prepared' and not manifest['issues'], 'frozen preparation blocked')
    expected=integrity['consumed']
    def bound(path, digest=None):
        if path.is_relative_to(prepared):
            require(str(path) in expected, 'unbound frozen source: '+str(path))
            require(digest is None or digest==expected[str(path)], 'source hash provenance mismatch')
            digest=expected[str(path)]
        return consume(path,digest)
    comparison=p.source_comparison(prepared,qualification,bound)
    write(output/'source-comparison.json',comparison)
    require(comparison['status']=='equivalent', 'A/A-fixed reconstruction failed')
    origin=Path(manifest['inputs']['v3']); verify_seal(origin,exact=False)
    frozen=consume(origin/'preparation.json')
    anchors=consume(prepared/'anchor-review.json')
    for variant in ('A','C'):
        # Both complete source and harness inventories are independently reproduced.
        files={}
        for group in GROUPS:
            source=origin/(variant+'T')/group
            require(o.inventory(source)==frozen['pairs'][variant+'T'][group], 'frozen source inventory drift')
            for name,digest in frozen['pairs'][variant+'T'][group].items():
                path=source/name; consume(path,digest); files[group+'/'+name]=path.read_bytes()
        replay=o.prep.replay(files,anchors[variant])
        for group in GROUPS:
            recorded=bound(prepared/'v4'/variant/'source-inventory.json')[group]
            require(o.inventory(prepared/'v4'/variant/group)==recorded, 'v4 inventory mismatch')
            require(set(recorded)=={n[len(group)+1:] for n in replay if n.startswith(group+'/')}, 'v4 source set mismatch')
            for name,digest in recorded.items():
                path=prepared/'v4'/variant/group/name; bound(path,digest)
                # Only private absolute include paths differ between anchor source and matched v4.
                require(p.b.v3.overhead.normalized(replay[group+'/'+name])==p.b.v3.overhead.normalized(path.read_bytes()), 'literal v4 replay mismatch: '+str(path))
        require(o.inventory(prepared/'v4'/variant)==manifest['outputs']['v4/'+variant], 'variant inventory drift')
    fixture=o.old.FIXTURE_ROOT/'3200x2400.png'
    # The retained report binds the execution preregistration, which in turn
    # records fixture identities. Do not assume it consumed the fixture directly.
    fixture_hashes={expected[str(fixture)]} if str(fixture) in expected else set()
    for name,digest in expected.items():
        if Path(name).name!='preregistration.json': continue
        registration=consume(Path(name),digest)
        if registration.get('prepared')!=str(prepared): continue
        value=registration.get('fixture_identities',{}).get(str(fixture))
        if value:
            require(registration.get('fixtures',{}).get(fixture.name)==value,'fixture registration disagreement')
            fixture_hashes.add(value)
    require(len(fixture_hashes)==1,'fixture provenance missing/ambiguous')
    fixture_hash=fixture_hashes.pop()
    consume(fixture,fixture_hash)
    write(output/'fixtures.json',{str(fixture):fixture_hash})
    write(output/'provenance.json',dict(evidence=str(evidence),prepared=str(prepared),origin=str(origin),qualification=str(qualification)))
    return prepared


def verify_generated(output, prepared):
    """Replay the emitted literal substitutions over every original source byte."""
    recorded=read(output/'anchors.json')
    expected_anchors=[]
    citations=[]
    for mode in ('baseline','validation'):
        for variant in ('A','C'):
            original=prepared/'v4'/variant; target=output/mode/variant
            require((target/'trace.h').read_bytes()==(original/'trace.h').read_bytes()+
                    (HEADER.encode() if mode=='validation' else b''),'private header mismatch')
            for group in GROUPS:
                inv=o.inventory(original/group)
                require(set(inv)==set(o.inventory(target/group)),'generated source inventory mismatch')
                for name in inv:
                    path=target/group/name; relative=group+'/'+name
                    expected=(original/group/name).read_bytes().replace(str(original/'trace.h').encode(),str(target/'trace.h').encode())
                    if mode=='validation' and (relative=='source/holonight-images/src/isolated/verification.cpp' or
                            variant=='C' and relative=='source/holonight-images/src/isolated/generation.cpp'):
                        expected,edits=instrument(expected.decode(),relative); expected=expected.encode()
                        expected_anchors += [dict(e,mode=mode,variant=variant) for e in edits]
                    require(path.read_bytes()==expected,'source transformation mismatch: '+str(path))
                    if path.suffix=='.cpp':
                        for number,line in enumerate(path.read_text().splitlines(),1):
                            if any(token in line for token in ('ValidationTrace::','StandbyTrace::','DeliveryTrace::')):
                                citations.append(dict(file=str(path),sha256=o.digest(path),line=number,text=line))
            require(read(target/'source-inventory.json')=={g:o.inventory(target/g) for g in GROUPS},'generated inventory drift')
    require(recorded==expected_anchors,'recorded anchor substitution mismatch')
    return citations


def prepare(evidence, output):
    o.fresh(output,evidence)
    result=dict(status='blocked',stage='provenance',measured_observations=0,launched_invocations=0)
    tracked={}; roots={}
    def consume(path,expected=None):
        digest=o.digest(path)
        require(expected is None or digest==expected, 'consumed hash mismatch: '+str(path))
        tracked[str(path)]=digest
        if path.suffix=='.json': return read(path)
        if path.suffix in ('.cpp','.h','.diff','.py'): return path.read_text()
        return path.read_bytes()
    try:
        write(output/'protocol.json',protocol())
        snapshots=output/'tools'; snapshots.mkdir()
        for path in (Path(__file__).resolve(), ROOT/'tests/test_preview_validation.py',
                     ROOT/'scripts/report-preview-predecode.py', ROOT/'scripts/prepare-preview-delivery-overhead.py'):
            consume(path)
            shutil.copy2(path,snapshots/path.name)
        roots[str(evidence)]=o.inventory(evidence)
        prepared=provenance(evidence,output,consume)
        roots[str(prepared)]=o.inventory(prepared)
        result['stage']='source_preparation'
        reviewed=[]
        for variant in ('A','C'):
            for name in ('verification.cpp','generation.cpp') if variant=='C' else ('verification.cpp',):
                relative='source/holonight-images/src/isolated/'+name
                _,edits=instrument((prepared/'v4'/variant/relative).read_text(),relative)
                reviewed.append(dict(variant=variant,file=relative,anchors=edits))
        write(output/'probe-review.json',reviewed)
        anchors=[]
        for mode in ('baseline','validation'):
            for variant in ('A','C'):
                original=prepared/'v4'/variant; target=output/mode/variant
                target.mkdir(parents=True)
                header=(original/'trace.h').read_bytes()
                (target/'trace.h').write_bytes(header+(HEADER.encode() if mode=='validation' else b''))
                for group in GROUPS:
                    shutil.copytree(original/group,target/group)
                    for path in sorted((target/group).rglob('*')):
                        if not path.is_file(): continue
                        old=path.read_bytes()
                        new=old.replace(str(original/'trace.h').encode(),str(target/'trace.h').encode())
                        relative=str(path.relative_to(target))
                        if mode=='validation' and relative in ('source/holonight-images/src/isolated/verification.cpp',
                                                               'source/holonight-images/src/isolated/generation.cpp'):
                            if relative.endswith('verification.cpp') or variant=='C':
                                new,edits=instrument(new.decode(),relative); new=new.encode()
                                anchors += [dict(x,mode=mode,variant=variant) for x in edits]
                        path.write_bytes(new)
                        if old!=new:
                            diff=''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),
                                                           fromfile=str(original/group/path.relative_to(target/group)),tofile=str(path)))
                            patch=target/'patches'/relative
                            patch.parent.mkdir(parents=True,exist_ok=True); patch.with_suffix(patch.suffix+'.diff').write_text(diff)
                write(target/'source-inventory.json',{g:o.inventory(target/g) for g in GROUPS})
        write(output/'anchors.json',anchors)
        write(output/'source-citations.json',verify_generated(output,prepared))
        result.update(status='prepared',stage='complete')
    except ERRORS as error:
        result['failure']=str(error)
    finally:
        checks={}
        for name,digest in tracked.items():
            try: checks[name]=o.digest(Path(name))==digest
            except OSError: checks[name]=False
        for name,inv in roots.items():
            try: checks[name]=o.inventory(Path(name))==inv
            except OSError: checks[name]=False
        if not all(checks.values()): result.update(status='blocked',integrity_failure='input drift')
        write(output/'integrity.json',dict(consumed=tracked,before=roots,checks=checks,passed=all(checks.values())))
        write(output/'assessment.json',result)
        (output/'ASSESSMENT.md').write_text('# A/C validation diagnostic preparation\n\nStatus: '+result['status']+'\n\n'+
            result.get('failure','')+'\n\nNo measurements, builds or previews were run by preparation. Historical evidence remains unchanged.\n')
        o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,default=DEFAULT)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=prepare(args.evidence.absolute(),args.output.absolute())
    print(result)
    sys.exit(result['status']!='prepared')
