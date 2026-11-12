#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build a diagnostic-only instrumented frozen transaction runtime (never timed).

Hooks inject cancellation at exact lifecycle boundaries. Production benchmark
sources and binaries remain untouched. Run the resulting executable as the user
against a separately protected runtime. Original A is diagnostic evidence only.
"""
import argparse
from pathlib import Path
import subprocess


def prepare(source, prefix, output):
    output.mkdir(parents=True, exist_ok=False)
    runtime = (source / 'src/isolated/runtime.cpp').read_text()
    replacements = {
        '    if (cancelled.load()) {': '    diagnosticHook("before-launch");\n    if (cancelled.load()) {',
        '    launched = true;': '    launched = true;\n    diagnosticHook("launched");',
        '    if (fileBytes(group + "/memory.max")':
            '    diagnosticHook("discovered");\n    if (fileBytes(group + "/memory.max")',
        '    check();  // Own': '    diagnosticHook("discovered");\n    check();  // Own',
        '    if (process.write("G", 1)': '    diagnosticHook("gate");\n    if (process.write("G", 1)',
        '    report = cleanup(operations, unit, group);':
            '    report = cleanup(operations, unit, group);\n    diagnosticCleanup(*report);',
    }
    # Corrected runtime observes cancellation immediately after discovery. Place
    # its hook before that check; original A has no such check.
    if '    check();  // Own' in runtime:
        del replacements['    if (fileBytes(group + "/memory.max")']
    for old, new in replacements.items():
        old, new = '\n' + old, '\n' + new
        if old in runtime:
            assert runtime.count(old) == 1
            runtime = runtime.replace(old, new)
    runtime = runtime.replace('namespace HolonightImages::Isolation {', '''namespace HolonightImages::Isolation {
void diagnosticHook(const char* phase);
void diagnosticCleanup(CleanupReport& report);''', 1)
    (output / 'runtime.cpp').write_text(runtime)
    (output / 'main.cpp').write_text(r'''// SPDX-License-Identifier: GPL-3.0-or-later
#include "runtime.h"
#include "cleanup.h"
#include <QCoreApplication>
#include <QElapsedTimer>
#include <QJsonDocument>
#include <QJsonObject>
#include <cstdio>
using namespace HolonightImages;
using namespace HolonightImages::Isolation;
namespace {
std::atomic_bool cancelled{false};
QString phase;
bool forceFailure = false;
int gates = 0, cleanups = 0;
QElapsedTimer diagnosticClock;
QJsonObject trace;
}
namespace HolonightImages::Isolation {
void diagnosticHook(const char* at) {
  trace[at] = diagnosticClock.nsecsElapsed() / 1000000.0;
  if (phase == at) cancelled.store(true);
  if (QString(at) == "gate") ++gates;
}
void diagnosticCleanup(CleanupReport& report) {
  ++cleanups;
  trace["scope"] = report.group;
  trace["cleanup_verified"] = report.verified;
  trace["cleanup_ms"] = report.elapsed;
  if (forceFailure) report.verified = false;
}
}
int main(int argc, char** argv) {
  QCoreApplication app(argc, argv);
  if (argc != 5) return 2;
  phase = argv[2];
  const bool corrected = QString(argv[3]) == "fixed";
  forceFailure = QString(argv[4]) == "force-failure";
  diagnosticClock.start();
  const auto result = dispatch(argv[1], {}, {}, cancelled);
  const bool before = phase == "before-launch";
  const bool ok = gates == 0 && cleanups == (before ? 0 : 1) &&
    result.status == (forceFailure && !before ? RuntimeStatus::CleanupFailure : RuntimeStatus::Cancelled);
  trace["phase"] = phase;
  trace["gate_count"] = gates;
  trace["cleanup_count"] = cleanups;
  trace["diagnostic"] = result.diagnostic;
  trace["passed"] = ok;
  std::puts(QJsonDocument(trace).toJson(QJsonDocument::Compact).constData());
  return corrected && !ok ? 1 : 0;
}
''')
    (output / 'CMakeLists.txt').write_text(f'''cmake_minimum_required(VERSION 3.25)
project(baseline_cancellation LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 23)
find_package(HolonightImages REQUIRED COMPONENTS Isolated)
add_executable(baseline-cancellation main.cpp runtime.cpp)
target_compile_options(baseline-cancellation PRIVATE -iquote "{source}/src/isolated")
target_link_libraries(baseline-cancellation PRIVATE HolonightImages::Isolated)
''')
    subprocess.run(['cmake', '-S', str(output), '-B', str(output / 'build'), '-G', 'Ninja',
                    '-DCMAKE_BUILD_TYPE=Release', f'-DCMAKE_PREFIX_PATH={prefix}'], check=True)
    subprocess.run(['cmake', '--build', str(output / 'build'), '-j4'], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('prefix', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    prepare(args.source.resolve(), args.prefix.resolve(), args.output.resolve())
