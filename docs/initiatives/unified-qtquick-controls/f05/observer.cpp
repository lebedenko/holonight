// SPDX-License-Identifier: GPL-3.0-or-later
// SPDX-FileCopyrightText: 2026 Andrii L <lebeden@gmail.com>
// Metadata only: never reads entered text or requests focus/frame updates.
#include "xdg-shell-client-protocol.h"

#include <QDateTime>
#include <QGuiApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QKeyEvent>
#include <QQuickItem>
#include <QQuickWindow>
#include <QTimer>

#include <atomic>
#include <cstdio>
#include <cstring>
#include <dlfcn.h>
#include <map>
#include <memory>
#include <wayland-client.h>

namespace {
QString id(const void* object) { return QString::number(reinterpret_cast<quintptr>(object), 16); }
void report(QJsonObject state) {
  state["time_ms"] = QDateTime::currentMSecsSinceEpoch();
  const auto bytes = QJsonDocument(state).toJson(QJsonDocument::Compact);
  fprintf(stderr, "F05 %s\n", bytes.constData());
}
class Observer : public QObject {
 public:
  explicit Observer(QObject* parent) : QObject(parent) {
    qApp->installEventFilter(this);
    auto* timer = new QTimer(this);
    connect(timer, &QTimer::timeout, this, [this] { sample(); });
    timer->start(100);
  }
  bool eventFilter(QObject* receiver, QEvent* event) override {
    if (event->type() == QEvent::Show) sample();
    if (event->type() != QEvent::KeyPress && event->type() != QEvent::KeyRelease) return false;
    auto* key = static_cast<QKeyEvent*>(event);
    if (key->key() == Qt::Key_Tab || key->key() == Qt::Key_Backtab)
      report({{"kind", "navigation"},
              {"receiver", id(receiver)},
              {"key", key->key() == Qt::Key_Tab ? "Tab" : "Backtab"},
              {"press", event->type() == QEvent::KeyPress}});
    return false;
  }

 private:
  QHash<QQuickWindow*, std::shared_ptr<std::atomic_uint64_t>> frames_;
  void sample() {
    report({{"kind", "application"},
            {"focusWindow", id(QGuiApplication::focusWindow())},
            {"state", QGuiApplication::applicationState()}});
    for (auto* window : QGuiApplication::allWindows()) {
      auto* quick = qobject_cast<QQuickWindow*>(window);
      if (!quick) continue;
      if (!frames_.contains(quick)) {
        auto frames = std::make_shared<std::atomic_uint64_t>(0);
        frames_[quick] = frames;
        connect(quick, &QQuickWindow::frameSwapped, quick, [frames] { ++*frames; }, Qt::DirectConnection);
        connect(quick, &QObject::destroyed, this, [this, quick] { frames_.remove(quick); });
      }
      report({{"kind", "window"},
              {"id", id(quick)},
              {"name", quick->objectName()},
              {"active", quick->isActive()},
              {"focusItem", id(quick->activeFocusItem())},
              {"width", quick->width()},
              {"height", quick->height()},
              {"dpr", quick->devicePixelRatio()},
              {"visible", quick->isVisible()},
              {"framesSwapped", double(frames_[quick]->load())}});
    }
  }
};
void start() {
  QTimer::singleShot(0, qApp, [] { new Observer(qApp); });
}
Q_COREAPP_STARTUP_FUNCTION(start)
struct Keyboard {
  wl_keyboard_listener original;
  wl_keyboard_listener observed;
};
struct Toplevel {
  xdg_toplevel_listener original;
  xdg_toplevel_listener observed;
};
struct Seat {
  wl_seat_listener original;
  wl_seat_listener observed;
};
std::map<wl_keyboard*, Keyboard> keyboards;
std::map<xdg_toplevel*, Toplevel> toplevels;
std::map<wl_seat*, Seat> seats;
void enter(void* data, wl_keyboard* keyboard, uint32_t serial, wl_surface* surface, wl_array* keys) {
  report({{"kind", "keyboard-enter"},
          {"keyboard", int(wl_proxy_get_id(reinterpret_cast<wl_proxy*>(keyboard)))},
          {"surface", surface ? int(wl_proxy_get_id(reinterpret_cast<wl_proxy*>(surface))) : 0}});
  keyboards.at(keyboard).original.enter(data, keyboard, serial, surface, keys);
}
void leave(void* data, wl_keyboard* keyboard, uint32_t serial, wl_surface* surface) {
  report({{"kind", "keyboard-leave"},
          {"surface", surface ? int(wl_proxy_get_id(reinterpret_cast<wl_proxy*>(surface))) : 0}});
  keyboards.at(keyboard).original.leave(data, keyboard, serial, surface);
}
void key(void* data, wl_keyboard* keyboard, uint32_t serial, uint32_t time, uint32_t code, uint32_t state) {
  if (code == 15) report({{"kind", "wayland-tab"}, {"pressed", state == WL_KEYBOARD_KEY_STATE_PRESSED}});
  keyboards.at(keyboard).original.key(data, keyboard, serial, time, code, state);
}
void configure(void* data, xdg_toplevel* toplevel, int32_t width, int32_t height, wl_array* states) {
  bool activated = false;
  const auto* values = static_cast<const uint32_t*>(states->data);
  for (size_t i = 0; i < states->size / sizeof(uint32_t); ++i) activated |= values[i] == XDG_TOPLEVEL_STATE_ACTIVATED;
  report({{"kind", "toplevel-configure"},
          {"id", int(wl_proxy_get_id(reinterpret_cast<wl_proxy*>(toplevel)))},
          {"width", width},
          {"height", height},
          {"activated", activated}});
  toplevels.at(toplevel).original.configure(data, toplevel, width, height, states);
}
void capabilities(void* data, wl_seat* seat, uint32_t caps) {
  report({{"kind", "seat-capabilities"}, {"keyboard", bool(caps & WL_SEAT_CAPABILITY_KEYBOARD)}});
  seats.at(seat).original.capabilities(data, seat, caps);
}
}  // namespace
extern "C" int wl_proxy_add_listener(wl_proxy* proxy, void (**implementation)(void), void* data) {
  using AddListener = int (*)(wl_proxy*, void (**)(void), void*);
  static auto original = reinterpret_cast<AddListener>(dlsym(RTLD_NEXT, "wl_proxy_add_listener"));
  const char* kind = wl_proxy_get_class(proxy);
  void (**observed)(void) = implementation;
  if (strcmp(kind, "wl_keyboard") == 0) {
    auto& entry = keyboards[reinterpret_cast<wl_keyboard*>(proxy)];
    entry.original = *reinterpret_cast<wl_keyboard_listener*>(implementation);
    entry.observed = entry.original;
    entry.observed.enter = enter;
    entry.observed.leave = leave;
    entry.observed.key = key;
    observed = reinterpret_cast<void (**)(void)>(&entry.observed);
  } else if (strcmp(kind, "xdg_toplevel") == 0) {
    auto& entry = toplevels[reinterpret_cast<xdg_toplevel*>(proxy)];
    entry.original = *reinterpret_cast<xdg_toplevel_listener*>(implementation);
    entry.observed = entry.original;
    entry.observed.configure = configure;
    observed = reinterpret_cast<void (**)(void)>(&entry.observed);
  } else if (strcmp(kind, "wl_seat") == 0) {
    auto& entry = seats[reinterpret_cast<wl_seat*>(proxy)];
    entry.original = *reinterpret_cast<wl_seat_listener*>(implementation);
    entry.observed = entry.original;
    entry.observed.capabilities = capabilities;
    observed = reinterpret_cast<void (**)(void)>(&entry.observed);
  }
  const int result = original(proxy, observed, data);
  if (observed != implementation)
    report(
        {{"kind", "listener"}, {"interface", kind}, {"id", int(wl_proxy_get_id(proxy))}, {"installed", result == 0}});
  return result;
}
