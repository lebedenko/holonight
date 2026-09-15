// SPDX-License-Identifier: GPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Andrii L <lebeden@gmail.com>
#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QTimer>

int main(int argc, char** argv) {
  QGuiApplication app(argc, argv);
  const bool holonight = app.arguments().contains(QStringLiteral("--hn"));
  const bool smoke = app.arguments().contains(QStringLiteral("--smoke"));
  QQmlApplicationEngine engine;
  // Same Loader/toggle lifecycle as WorkspaceWindow, with provider behavior removed.
  QByteArray source = R"(
import QtQuick
import QtQuick.Controls as Controls
%IMPORT%
%WINDOW% {
    id: root
    objectName: "workspace"
    width: 640; height: 400; visible: true
    title: "F05 reduced workspace"
    Loader {
        id: settingsLoader
        active: %SMOKE%
        sourceComponent: %WINDOW% {
            id: settings
            objectName: "settings"
            width: 520; height: 360
            visible: %SMOKE%
            title: "F05 reduced settings"
            Column {
                anchors.centerIn: parent
                spacing: 16
                Controls.SpinBox { objectName: "contextWindow"; editable: true; from: 1; to: 32768; value: 4096 }
                Controls.Slider { objectName: "temperature"; from: 0; to: 2; value: 1 }
                Controls.Switch { objectName: "option"; text: "Option" }
                Controls.Button { text: "Close settings"; onClicked: settings.close() }
                Controls.Button { text: "Quit fixture"; onClicked: Qt.quit() }
            }
        }
    }
    Controls.Button {
        anchors.centerIn: parent
        text: "Open / close settings"
        onClicked: {
            settingsLoader.active = true
            settingsLoader.item.visible = !settingsLoader.item.visible
            if (settingsLoader.item.visible) {
                // User-triggered lifecycle, never invoked by the smoke runner.
                settingsLoader.item.raise()
                settingsLoader.item.requestActivate()
            }
        }
    }
}
)";
  source.replace("%IMPORT%", holonight ? "import Holonight.Controls" : "");
  source.replace("%WINDOW%", holonight ? "HnApplicationWindow" : "Window");
  source.replace("%SMOKE%", smoke ? "true" : "false");
  engine.loadData(source);
  if (engine.rootObjects().isEmpty()) return 2;
  if (smoke) QTimer::singleShot(1200, &app, &QCoreApplication::quit);
  return app.exec();
}
