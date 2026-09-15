#!/usr/bin/env python3
"""Check opt-in navigation observation without live keyboard or focus interaction."""
import argparse
import json
import os
from pathlib import Path
import subprocess

SOURCE = r'''
#include <QGuiApplication>
#include <QQuickWindow>
#include <QTimer>
#include <QKeyEvent>
#include <cstdio>
class Receiver : public QObject {
 bool event(QEvent* event) override {
  if (event->type() == QEvent::KeyPress) {
   auto* key = static_cast<QKeyEvent*>(event);
   key->setAccepted(key->key() == Qt::Key_Tab);
   return true;
  }
  return QObject::event(event);
 }
};
int main(int argc, char** argv) {
 QGuiApplication app(argc,argv);
 QQuickWindow window; window.resize(320,120); window.show();
 Receiver receiver;
 QTimer::singleShot(250,&app,[&] {
  for(int code : {int(Qt::Key_Tab), int(Qt::Key_Backtab), int(Qt::Key_A)}) {
   QKeyEvent event(QEvent::KeyPress,code,Qt::NoModifier,"DO_NOT_RECORD_FORM_TEXT");
   QCoreApplication::sendEvent(&receiver,&event);
   if(event.isAccepted() != (code==Qt::Key_Tab)) std::abort();
  }
  puts("OBSERVER_FIXTURE_OK");
  QTimer::singleShot(50,&app,&QCoreApplication::quit);
 });
 return app.exec();
}
'''

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prefix', type=Path)
    parser.add_argument('logs', type=Path)
    args = parser.parse_args()
    args.logs.mkdir(parents=True, exist_ok=True)
    source = args.logs / 'observer-check.cpp'
    binary = args.logs / 'observer-check'
    source.write_text(SOURCE)
    flags = subprocess.check_output(['pkg-config', '--cflags', '--libs', 'Qt6Quick'], text=True).split()
    subprocess.run(['g++', '-fPIC', '-std=c++23', str(source), *flags, '-o', str(binary)], check=True)
    for style in ('Holonight', 'Fusion'):
        for scale in ('1', '1.25'):
            for enabled in (False, True):
                env = dict(os.environ, QT_QPA_PLATFORM='offscreen', QT_QUICK_BACKEND='software',
                           QT_QUICK_CONTROLS_STYLE=style, QT_SCALE_FACTOR=scale)
                for key in ('LD_PRELOAD', 'HOLONIGHT_SESSION_DIAGNOSTICS', 'HOLONIGHT_SESSION_GEOMETRY'):
                    env.pop(key, None)
                if enabled:
                    env.update(LD_PRELOAD=str(args.prefix / 'lib/session-diagnostics.so'), HOLONIGHT_SESSION_DIAGNOSTICS='1')
                result = subprocess.run([str(binary)], env=env, capture_output=True, text=True, timeout=10)
                output = result.stdout + result.stderr
                (args.logs / f'{style}-{scale}-{enabled}.log').write_text(output)
                assert result.returncode == 0 and 'OBSERVER_FIXTURE_OK' in output
                assert 'DO_NOT_RECORD_FORM_TEXT' not in output
                records = [json.loads(line.split('HN_SESSION ', 1)[1]) for line in output.splitlines() if 'HN_SESSION ' in line]
                if not enabled:
                    assert not records
                    continue
                keys = [record['key'] for record in records if record['kind'] == 'qt-navigation-before']
                assert keys == ['Tab', 'Backtab'], keys
                assert len([record for record in records if record['kind'] == 'qt-navigation-after-delivery']) == 2
                assert all(record['finalAcceptance'] == 'unavailable' for record in records if record['kind'] == 'qt-navigation-after-delivery')
                assert any(record.get('dpr') == float(scale) for record in records if record['kind'] == 'window')
    print('Observer on/off, actual DPR, navigation forwarding/acceptance and text exclusion: 8/8 passed')

if __name__ == '__main__':
    main()
