#!/usr/bin/env python3
"""Prepare private A/C helper-startup probes. No build or execution actions."""
import argparse
import difflib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import types

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('helper_validation', ROOT/'scripts/prepare-preview-validation.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
o, require, read, write = v.o, v.require, v.read, v.write
GROUPS = v.GROUPS
RUNTIME = 'source/holonight-images/src/isolated/runtime.cpp'
ERRORS = (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError)
COMBINATIONS = [(variant, arm) for arm in ('baseline', 'instrumented', 'captured') for variant in ('A', 'C')]
HEADER = r'''
// Private parent-side helper startup stream; runtime-generation identity is unproven.
#include <QFile>
#include <QJsonDocument>
#include <QJsonObject>
namespace HelperStartupTrace {
inline std::atomic<unsigned long long> sequence{1};
inline thread_local unsigned long long parent=0;
inline QString boot() {
  static const QString value=[] { QFile f("/proc/sys/kernel/random/boot_id");
    return f.open(QIODevice::ReadOnly) ? QString::fromUtf8(f.readAll().trimmed()) : QString{}; }();
  return value;
}
inline QString host() {
  static const QString value=[] { char name[256]{};
    return gethostname(name,sizeof(name)-1)==0 ? QString::fromUtf8(name) : QString{}; }();
  return value;
}
struct Scope {
  const char* operation;
  unsigned long long span=sequence.fetch_add(1), previous=parent;
  StandbyTrace::Context context=StandbyTrace::current;
  int exceptions=std::uncaught_exceptions();
  bool active=true;
  void event(const char* edge) const {
    auto id=[](unsigned long long n)->QJsonValue { return n ? QJsonValue(QString::number(n)) : QJsonValue(QJsonValue::Null); };
    auto text=[](const QString& s)->QJsonValue { return s.isEmpty() ? QJsonValue(QJsonValue::Null) : QJsonValue(s); };
    // Timestamp precedes serialization; emission overhead remains unmeasured.
    const auto ns=DeliveryTrace::now();
    QJsonObject record{{"version",1},{"ns",QString::number(ns)},
      {"pid",static_cast<int>(getpid())},{"tid",static_cast<int>(syscall(SYS_gettid))},
      {"invocation",text(qEnvironmentVariable("HOLONIGHT_HELPER_INVOCATION"))},
      {"host",text(host())},{"boot",text(boot())},{"clock","CLOCK_MONOTONIC"},
      {"service",id(context.service)},{"observation",id(context.observation)},
      {"job",id(context.job)},{"worker",id(context.worker)},{"preparation",id(context.preparation)},
      {"request_generation",id(context.delivery_generation)},{"runtime_generation",QJsonValue(QJsonValue::Null)},
      {"span",id(span)},{"parent",id(previous)},{"operation",operation},{"edge",edge},
      {"outcome",edge[0]=='b' ? "unavailable" : (std::uncaught_exceptions()>exceptions ? "exception" : "returned")}};
    const auto line=QByteArray("HELPER_STARTUP ")+QJsonDocument(record).toJson(QJsonDocument::Compact)+'\n';
    auto ignored=::write(2,line.constData(),line.size()); (void)ignored;
  }
  explicit Scope(const char* name):operation(name) { event("begin"); parent=span; }
  void finish() { if(active) { event("end"); parent=previous; active=false; } }
  ~Scope() { finish(); }
  Scope(const Scope&)=delete;
  Scope& operator=(const Scope&)=delete;
};
template<class F> auto measure(const char* name,F operation) { Scope scope(name); return operation(); }
}
'''


def protocol():
    rows = []
    for block in (None, *range(5)):
        order = COMBINATIONS if block is None else COMBINATIONS[block % 6:]+COMBINATIONS[:block % 6]
        if block is not None and block % 2: order = list(reversed(order))
        rows += [dict(variant=a, arm=b, block=block, warmup=block is None,
                      observations=1 if block is None else 5, fixture='3200x2400.png') for a,b in order]
    return dict(schedule=rows, invocations=36, measured_observations=150, warmups=6,
                timeout_seconds=30, termination_grace_seconds=5, retries=0,
                stop_on_first=['correctness','lifecycle','integrity','recorder','cleanup'],
                recorder=v.protocol()['recorder'],
                predicates='Original harness pixel and metadata latency predicates unchanged.',
                invocation_identity='Set HOLONIGHT_HELPER_INVOCATION uniquely for every future invocation; absent remains null.',
                interpretation='Descriptive instrumentation/recorder comparisons only; subtract no overhead. '
                'Non-runnable time identifies no blocking cause. No optimization or qualification reassessment.')


def instrument(text, variant):
    require(variant in ('A','C'), 'unsupported variant')
    anchors = []
    def edit(old,new,operation):
        nonlocal text
        text = v.replace(text,old,new,anchors,RUNTIME)
        anchors[-1]['operation'] = operation
    def after(anchor,addition,operation): edit(anchor,anchor+'\n'+addition,operation)
    def before(anchor,addition,operation): edit(anchor,addition+'\n'+anchor,operation)
    broad = ('    StandbyTrace::event("helper_prepare", "begin", &process);' if variant=='A'
             else '  StandbyTrace::Scope trace("helper_prepare", this, -1);')
    after(broad,'    HelperStartupTrace::Scope helper_root("preparation");\n'
          '    HelperStartupTrace::Scope helper_resolution("runtime_lease_resolution");','preparation')
    cancel = '    if (cancelled.load()) {' if variant=='A' else '    if (cancelled->load()) {'
    # This anchor appears once in each frozen preparation implementation.
    before(cancel,'    helper_resolution.finish();\n    HelperStartupTrace::Scope helper_launchers("launcher_checks");','runtime_lease_resolution')
    before('    unit = "holonight-images-" + QUuid::createUuid().toString(QUuid::Id128) + ".scope";',
           '    helper_launchers.finish();\n    HelperStartupTrace::Scope helper_command("command_environment_setup");','launcher_checks')
    before('    process.start("/usr/bin/systemd-run", command);','    helper_command.finish();','command_environment_setup')
    edit('    process.start("/usr/bin/systemd-run", command);',
         '    HelperStartupTrace::measure("process_start", [&] { process.start("/usr/bin/systemd-run", command); });','process_start')
    edit('    if (!process.waitForStarted(1000)) {',
         '    if (!HelperStartupTrace::measure("wait_for_started", [&] { return process.waitForStarted(1000); })) {','wait_for_started')
    before('    while (group.isEmpty()) {','    HelperStartupTrace::Scope helper_discovery("scope_discovery_polling");','scope_discovery_polling')
    check = '    check();  // Own the scope before cancellation; keep the trusted input gate closed.' if variant=='A' else '    check();\n    if (fileBytes(group + "/memory.max")'
    if variant=='A':
        before(check,'    helper_discovery.finish();\n    HelperStartupTrace::Scope helper_limits("limit_verification");','limit_verification')
    else:
        edit(check,'    helper_discovery.finish();\n    HelperStartupTrace::Scope helper_limits("limit_verification");\n'+check,'limit_verification')
    if variant=='A':
        before('    auto receive = [&](qint64 size) {','    helper_limits.finish();\n    HelperStartupTrace::Scope helper_receive_setup("receive_setup");','receive_setup')
    before('    if (process.write("G", 1) != 1) {',
           ('    helper_receive_setup.finish();' if variant=='A' else '    helper_limits.finish();')+
           '\n    HelperStartupTrace::Scope helper_gate("gate_write_flush");','gate_write_flush')
    # Match the gate flush and following try, not later transport flushes.
    after('    process.waitForBytesWritten(5);\n    try {',
          '      helper_gate.finish();\n      HelperStartupTrace::Scope helper_marker("readiness_marker_receive");','readiness_marker_receive')
    if variant=='C':
        # Separate receive from validation without changing parse or validation expressions.
        edit('    if (session) {\n      const auto length = qFromBigEndian<quint32>(receive(4).constData());',
             '    if (session) {\n      HelperStartupTrace::Scope helper_session("session_readiness");\n'
             '      HelperStartupTrace::Scope helper_length("session_readiness_length");\n'
             '      const auto length = qFromBigEndian<quint32>(receive(4).constData());','session_readiness')
        before('      const auto ready = parseControl(receive(length));','      helper_length.finish();','session_readiness_length')
        edit('      const auto ready = parseControl(receive(length));',
             '      const auto helper_payload = HelperStartupTrace::measure("session_readiness_payload_receive", [&] { return receive(length); });\n'
             '      HelperStartupTrace::Scope helper_control("session_readiness_control_validation");\n'
             '      const auto ready = parseControl(helper_payload);','session_readiness_payload_receive')
        before('    result.startup = elapsed.elapsed();','    HelperStartupTrace::Scope helper_final("final_bookkeeping");','final_bookkeeping')
        after('    prepared = true;','    helper_final.finish();\n    helper_root.finish();','preparation_end')
    else:
        before('    StandbyTrace::event("helper_ready", "point", &process);',
               '    HelperStartupTrace::Scope helper_final("final_bookkeeping");','final_bookkeeping')
        after('    result.startup = elapsed.elapsed();','    helper_final.finish();\n    helper_root.finish();','preparation_end')
    return text,anchors


def reconstruct(text, anchors):
    for edit in reversed(anchors):
        old,new=edit['anchor'],edit['replacement']
        require(text.count(new)==1, 'missing/duplicate reverse anchor')
        text=text.replace(new,old,1)
    return text


def provenance(evidence, verification, output, consume):
    o.check_output(evidence)
    for name,digest in read(evidence/'seal.json').items(): consume(o.prep.child(evidence,name),digest)
    consume(evidence/'seal.json')
    require(consume(evidence/'assessment.json')['status']=='complete','cold-start assessment blocked')
    record=consume(verification)
    require(record['status']=='passed' and record['assessment_seal']==o.digest(evidence/'seal.json'),
            'independent verification binding mismatch')
    integrity=consume(evidence/'integrity.json')
    require(integrity['passed'],'cold-start integrity failed')
    for name,digest in integrity['consumed'].items(): consume(Path(name),digest)
    # Reuse the literal A reconstruction and independent A/C inventory/anchor replay.
    predecode=[Path(n).parent for n in integrity['consumed'] if n.endswith('/source-comparison.json')]
    require(len(predecode)==1,'ambiguous source provenance')
    prepared=v.provenance(predecode[0],output,consume)
    require(consume(output/'source-comparison.json')==consume(evidence/'source-relationship.json'),
            'cold-start source relationship mismatch')
    for name in ('source-citations.json','raw-citations.json'):
        records=consume(evidence/name)
        if isinstance(records,dict): records=[row for rows in records.values() for row in rows]
        for citation in records:
            path=Path(citation['file']); consume(path,citation['sha256'])
            if 'text' in citation and 'line' in citation:
                require(path.read_text().splitlines()[citation['line']-1]==citation['text'],'citation mismatch')
    return prepared


def generated(output, prepared):
    anchors=[]; citations=[]
    for mode in ('baseline','instrumented'):
        for variant in ('A','C'):
            original=prepared/'v4'/variant; target=output/mode/variant
            require((target/'trace.h').read_bytes()==(original/'trace.h').read_bytes()+
                    (HEADER.encode() if mode=='instrumented' else b''),'header mismatch')
            for group in GROUPS:
                inv=o.inventory(original/group)
                require(set(inv)==set(o.inventory(target/group)), 'source set mismatch')
                for name in inv:
                    relative=group+'/'+name; path=target/relative
                    expected=(original/relative).read_bytes().replace(str(original/'trace.h').encode(),str(target/'trace.h').encode())
                    if mode=='instrumented' and relative==RUNTIME:
                        new,edits=instrument(expected.decode(),variant)
                        require(reconstruct(new,edits)==expected.decode(),'reverse reconstruction mismatch')
                        expected=new.encode(); anchors += [dict(e,mode=mode,variant=variant) for e in edits]
                    require(path.read_bytes()==expected,'generated source mismatch: '+str(path))
                    if path.suffix=='.cpp':
                        for line,text in enumerate(path.read_text().splitlines(),1):
                            if any(t in text for t in ('HelperStartupTrace::','StandbyTrace::','DeliveryTrace::')):
                                citations.append(dict(file=str(path),sha256=o.digest(path),line=line,text=text))
            require(read(target/'source-inventory.json')=={g:o.inventory(target/g) for g in GROUPS},'inventory mismatch')
    require(read(output/'anchors.json')==anchors,'anchor map mismatch')
    return citations


def prepare(evidence, verification, output):
    evidence,verification,output=(p.absolute() for p in (evidence,verification,output))
    # Refuse nesting in any recorded build package before creating a destination.
    # This also protects ancestors of source/harness subtrees from new entries.
    protected=set()
    try:
        for name in read(evidence/'integrity.json')['consumed']:
            path=Path(name).absolute()
            if path.is_relative_to(ROOT/'build'):
                parts=path.relative_to(ROOT/'build').parts
                if parts: protected.add(ROOT/'build'/parts[0])
    except (OSError,ValueError,KeyError,TypeError): pass
    o.fresh(output,evidence,verification,*protected)
    tracked={}; roots={}; result=dict(status='blocked',warning='UNCOMPILED, UNEXECUTED',launched_invocations=0)
    def consume(path,expected=None):
        path=path.absolute(); require(path==path.resolve(),'symlink input')
        digest=o.digest(path)
        require(expected is None or expected==digest,'consumed hash mismatch: '+str(path))
        require(str(path) not in tracked or tracked[str(path)]==digest,'input drift: '+str(path))
        tracked[str(path)]=digest
        if path.suffix=='.json': return read(path)
        data=path.read_bytes()
        try: return data.decode()
        except UnicodeDecodeError: return data
    try:
        write(output/'protocol.json',protocol())
        snapshots=output/'tools'; snapshots.mkdir()
        paths=[Path(__file__).resolve(),ROOT/'scripts/analyze-preview-helper-startup.py',
               ROOT/'scripts/verify-preview-helper-startup.py',ROOT/'tests/test_preview_helper_startup.py',
               ROOT/'docs/initiatives/delivery-tracing-v4.md']
        # Snapshot the imported offline tool closure, including modules loaded by spec.
        pending=[v]; seen=set()
        while pending:
            m=pending.pop()
            if id(m) in seen: continue
            seen.add(id(m))
            path=Path(getattr(m,'__file__','/')).resolve()
            if path.parent!=ROOT/'scripts': continue
            paths.append(path)
            pending += [x for x in vars(m).values() if isinstance(x,types.ModuleType)]
        for path in sorted(set(paths)):
            consume(path); shutil.copy2(path,snapshots/path.name)
        roots[str(evidence)]=o.inventory(evidence)
        prepared=provenance(evidence,verification,output,consume)
        roots[str(prepared)]=o.inventory(prepared)
        for variant in ('A','C'):
            original=prepared/'v4'/variant
            for name,digest in o.inventory(original).items(): consume(original/name,digest)
        require(not output.is_relative_to(prepared) and not prepared.is_relative_to(output),'overlapping sources')
        anchors=[]
        # Review both variants before emitting either instrumented tree.
        for variant in ('A','C'): instrument((prepared/'v4'/variant/RUNTIME).read_text(),variant)
        for mode in ('baseline','instrumented'):
            for variant in ('A','C'):
                original=prepared/'v4'/variant; target=output/mode/variant
                target.mkdir(parents=True)
                (target/'trace.h').write_bytes((original/'trace.h').read_bytes()+(HEADER.encode() if mode=='instrumented' else b''))
                diffs=[]
                for group in GROUPS:
                    shutil.copytree(original/group,target/group)
                    for path in sorted((target/group).rglob('*')):
                        if not path.is_file(): continue
                        old=path.read_bytes(); new=old.replace(str(original/'trace.h').encode(),str(target/'trace.h').encode())
                        if mode=='instrumented' and str(path.relative_to(target))==RUNTIME:
                            text,edits=instrument(new.decode(),variant); new=text.encode()
                            anchors += [dict(e,mode=mode,variant=variant) for e in edits]
                        path.write_bytes(new)
                        if old!=new:
                            diffs.extend(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),
                                fromfile=str(original/path.relative_to(target)),tofile=str(path)))
                (target/'overlay.diff').write_text(''.join(diffs))
                write(target/'source-inventory.json',{g:o.inventory(target/g) for g in GROUPS})
        write(output/'anchors.json',anchors)
        write(output/'probe-to-source.json',generated(output,prepared))
        write(output/'inputs.json',dict(evidence=str(evidence),verification=str(verification),prepared=str(prepared)))
        result['status']='prepared'
    except ERRORS as error: result['failure']=str(error)
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
        (output/'ASSESSMENT.md').write_text('# Private helper-startup diagnostic\n\n**UNCOMPILED, UNEXECUTED**\n\n'+
            json.dumps(result,indent=2)+'\n\nNo optimization selected. Qualification remains failed at 78/80 gates.\n')
        o.seal(output)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('evidence','verification','output'): parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args(); result=prepare(args.evidence,args.verification,args.output)
    print(result); sys.exit(result['status']!='prepared')
