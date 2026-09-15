// SPDX-License-Identifier: GPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Andrii L <lebeden@gmail.com>

// Opt-in Batch 6 observer. Never reads text, synthesizes input, or changes
// focus.
#include <QColor>
#include <QCoreApplication>
#include <QDateTime>
#include <QGuiApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QKeyEvent>
#include <QQmlContext>
#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickWindow>
#include <QTimer>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <map>
#include <wayland-client.h>

namespace {
bool enabled() {
  return qEnvironmentVariable("HOLONIGHT_SESSION_DIAGNOSTICS") == "1";
}
QString identity(QObject *object) {
  return object ? QString::number(reinterpret_cast<quintptr>(object), 16) +
                      ":" + object->metaObject()->className()
                : QStringLiteral("null");
}
void report(QJsonObject state) {
  state["time_ms"] = QDateTime::currentMSecsSinceEpoch();
  const auto bytes = QJsonDocument(state).toJson(QJsonDocument::Compact);
  fprintf(stderr, "HN_SESSION %s\n", bytes.constData());
  fflush(stderr);
}
QJsonObject focus() {
  auto *window = qobject_cast<QQuickWindow *>(QGuiApplication::focusWindow());
  auto *item = window ? window->activeFocusItem() : nullptr;
  auto *context = item ? qmlContext(item) : nullptr;
  return {{"applicationState", QGuiApplication::applicationState()},
          {"focusWindow", identity(window)},
          {"activeFocusItem", identity(item)},
          {"activeFocusOrigin",
           context ? context->baseUrl().toString() : QString{}}};
}
class Observer : public QObject {
public:
  explicit Observer(QObject *parent) : QObject(parent) {
    auto *timer = new QTimer(this);
    connect(timer, &QTimer::timeout, this, [this] { sample(); });
    timer->start(100);
    qApp->installEventFilter(this);
  }
  bool eventFilter(QObject *receiver, QEvent *event) override {
    if (event->type() != QEvent::KeyPress &&
        event->type() != QEvent::KeyRelease)
      return false;
    auto *keyEvent = static_cast<QKeyEvent *>(event);
    if (keyEvent->key() != Qt::Key_Tab && keyEvent->key() != Qt::Key_Backtab)
      return false;
    auto state = focus();
    state["kind"] = "qt-navigation-before";
    state["receiver"] = identity(receiver);
    state["key"] = keyEvent->key() == Qt::Key_Backtab ? "Backtab" : "Tab";
    state["press"] = event->type() == QEvent::KeyPress;
    state["acceptedBefore"] = event->isAccepted();
    report(state);
    QTimer::singleShot(0, this, [] {
      auto after = focus();
      after["kind"] = "qt-navigation-after-delivery";
      // Event filters run before dispatch. Never label a queued focus sample as
      // the event's final acceptance; the event no longer exists at this point.
      after["finalAcceptance"] = "unavailable";
      report(after);
    });
    return false;
  }

private:
  QHash<QString, QByteArray> previous_;
  void changed(QJsonObject state) {
    const auto key = state["id"].toString();
    const auto bytes = QJsonDocument(state).toJson(QJsonDocument::Compact);
    if (previous_.value(key) == bytes)
      return;
    previous_[key] = bytes;
    report(state);
  }
  void walk(QQuickItem *item) {
    const auto bounds =
        item->mapRectToScene(QRectF(0, 0, item->width(), item->height()));
    QJsonObject state{{"kind", "item"},
                      {"id", identity(item)},
                      {"parent", identity(item->parentItem())},
                      {"x", item->x()},
                      {"y", item->y()},
                      {"width", item->width()},
                      {"height", item->height()},
                      {"sceneX", bounds.x()},
                      {"sceneY", bounds.y()},
                      {"sceneWidth", bounds.width()},
                      {"sceneHeight", bounds.height()},
                      {"implicitWidth", item->implicitWidth()},
                      {"implicitHeight", item->implicitHeight()},
                      {"scale", item->scale()},
                      {"clip", item->clip()},
                      {"visible", item->isVisible()},
                      {"opacity", item->opacity()},
                      {"enabled", item->isEnabled()}};
    if (auto *context = qmlContext(item))
      state["origin"] = context->baseUrl().toString();
    const auto color = item->property("color");
    if (color.canConvert<QColor>())
      state["color"] = color.value<QColor>().name(QColor::HexArgb);
    changed(state);
    for (auto *child : item->childItems())
      walk(child);
  }
  void sample() {
    auto state = focus();
    state["id"] = "application";
    state["kind"] = "focus";
    changed(state);
    for (auto *window : QGuiApplication::allWindows()) {
      auto *quick = qobject_cast<QQuickWindow *>(window);
      if (!quick)
        continue;
      changed({{"kind", "window"},
               {"id", identity(quick)},
               {"visible", quick->isVisible()},
               {"active", quick->isActive()},
               {"activeFocusItem", identity(quick->activeFocusItem())},
               {"width", quick->width()},
               {"height", quick->height()},
               {"dpr", quick->devicePixelRatio()}});
      if (qEnvironmentVariable("HOLONIGHT_SESSION_GEOMETRY") == "1")
        walk(quick->contentItem());
    }
  }
};
void start() {
  if (enabled())
    QTimer::singleShot(0, qApp, [] { new Observer(qApp); });
}
Q_COREAPP_STARTUP_FUNCTION(start)

struct KeyboardObserver {
  wl_keyboard_listener original;
  wl_keyboard_listener observed;
};
auto &keyboards() {
  static std::map<wl_keyboard *, KeyboardObserver> listeners;
  return listeners;
}
void enter(void *data, wl_keyboard *keyboard, uint32_t serial,
           wl_surface *surface, wl_array *keys) {
  report(
      {{"kind", "wayland-enter"},
       {"surface", QString::number(reinterpret_cast<quintptr>(surface), 16)}});
  keyboards().at(keyboard).original.enter(data, keyboard, serial, surface,
                                          keys);
}
void leave(void *data, wl_keyboard *keyboard, uint32_t serial,
           wl_surface *surface) {
  report(
      {{"kind", "wayland-leave"},
       {"surface", QString::number(reinterpret_cast<quintptr>(surface), 16)}});
  keyboards().at(keyboard).original.leave(data, keyboard, serial, surface);
}
void key(void *data, wl_keyboard *keyboard, uint32_t serial, uint32_t time,
         uint32_t code, uint32_t state) {
  // Linux evdev KEY_TAB only. Do not inspect or log any other key.
  if (code == 15)
    report({{"kind", "wayland-tab"},
            {"pressed", state == WL_KEYBOARD_KEY_STATE_PRESSED},
            {"protocolTime", double(time)}});
  keyboards().at(keyboard).original.key(data, keyboard, serial, time, code,
                                        state);
}
} // namespace

extern "C" int wl_proxy_add_listener(wl_proxy *proxy,
                                     void (**implementation)(void),
                                     void *data) {
  using Original = int (*)(wl_proxy *, void (**)(void), void *);
  static auto original =
      reinterpret_cast<Original>(dlsym(RTLD_NEXT, "wl_proxy_add_listener"));
  if (enabled() && strcmp(wl_proxy_get_class(proxy), "wl_keyboard") == 0) {
    auto *keyboard = reinterpret_cast<wl_keyboard *>(proxy);
    auto &listener = keyboards()[keyboard];
    listener.original =
        *reinterpret_cast<wl_keyboard_listener *>(implementation);
    listener.observed = listener.original;
    listener.observed.enter = enter;
    listener.observed.leave = leave;
    listener.observed.key = key;
    const auto result = original(
        proxy, reinterpret_cast<void (**)(void)>(&listener.observed), data);
    report({{"kind", "wayland-keyboard-listener"}, {"installed", result == 0}});
    return result;
  }
  return original(proxy, implementation, data);
}
