#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")
from gi.repository import Gtk, GLib, Gdk, AyatanaAppIndicator3 as AppIndicator3
import argparse, os, time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.txt")
ICON_DIR = os.path.join(SCRIPT_DIR, "icons")
ICON_NAME = "coffee-cup"

DEFAULTS = {
    "BREAK_INTERVAL_MIN": 30,
    "BREAK_DURATION_MIN": 5,
    "MICRO_INTERVAL_MIN": 10,
    "MICRO_DURATION_SEC": 20,
    "BREAK_WARN_1_MIN": 2,
    "BREAK_WARN_2_MIN": 1,
    "BREAK_COUNTDOWN_SEC": 30,
    "MICRO_COUNTDOWN_SEC": 10,
    "POSTPONE_MIN": 2,
    "MICRO_POSTPONE_MIN": 1,
}

# -d/--debug: use these instead of config.txt, with every _MIN value
# treated as seconds (UNIT_SEC=1) so a full cycle takes well under a minute.
DEBUG_DEFAULTS = {
    "BREAK_INTERVAL_MIN": 20,
    "BREAK_DURATION_MIN": 6,
    "MICRO_INTERVAL_MIN": 8,
    "MICRO_DURATION_SEC": 4,
    "BREAK_WARN_1_MIN": 10,
    "BREAK_WARN_2_MIN": 5,
    "BREAK_COUNTDOWN_SEC": 4,
    "MICRO_COUNTDOWN_SEC": 2,
    "POSTPONE_MIN": 2,
    "MICRO_POSTPONE_MIN": 1,
}

UNIT_SEC = 60      # multiplier turning a "_MIN" value into seconds
UNIT_LABEL = "min"  # unit shown on Postpone buttons

def build_css():
    base_pt = system_font_pt()
    button_pt = base_pt
    title_pt = base_pt * 2.4
    countdown_pt = base_pt * 5.4
    pause_button_pt = base_pt * 1.2
    outline = """
    -2px -2px 0 rgba(0, 0, 0, 1),
     2px -2px 0 rgba(0, 0, 0, 1),
    -2px  2px 0 rgba(0, 0, 0, 1),
     2px  2px 0 rgba(0, 0, 0, 1),
     0px   0px  6px  rgba(0, 0, 0, 0.95),
     0px   0px  12px rgba(0, 0, 0, 0.85),
     0px   0px  20px rgba(0, 0, 0, 0.7)"""
    return f"""
window.notify-popup {{
  border-radius: 8px;
  background-color: rgba(20, 20, 20, 0.3);
}}
window.notify-popup label {{
  color: #ffffff;
  text-shadow: {outline};
}}
window.notify-popup button {{
  font-size: {button_pt}pt;
  padding: 2px 9px;
  min-height: 0;
  color: #ffffff;
  text-shadow: {outline};
}}
window.pause-window label.title {{ font-size: {title_pt}pt; }}
window.pause-window label.countdown {{ font-size: {countdown_pt}pt; font-weight: bold; }}
window.pause-window button {{ font-size: {pause_button_pt}pt; padding: 8px 22px; }}
""".encode()


def load_config():
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip().upper()
                if key in DEFAULTS:
                    try:
                        cfg[key] = int(val.strip())
                    except ValueError:
                        pass
    else:
        with open(CONFIG_PATH, "w") as f:
            for k, v in DEFAULTS.items():
                f.write(f"{k}={v}\n")
    return cfg


FADE_IN_MS = 150
FADE_OUT_MS = 200
FADE_STEP_MS = 15


def system_font_pt():
    font_name = Gtk.Settings.get_default().get_property("gtk-font-name") or "Sans 10"
    try:
        return float(font_name.rsplit(" ", 1)[-1])
    except ValueError:
        return 10.0


class NotifyPopup(Gtk.Window):
    def __init__(self, big, small, postpone_min, on_skip, on_postpone, is_break):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)
        Gtk.Widget.set_opacity(self, 0.0)
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_resizable(False)
        self.set_size_request(210, -1)
        self.get_style_context().add_class("notify-popup")

        self.label = Gtk.Label()
        self.set_text(big, small)
        self.label.set_line_wrap(True)
        self.label.set_justify(Gtk.Justification.CENTER)
        self.label.set_margin_start(10)
        self.label.set_margin_end(10)
        self.label.set_margin_top(8)
        self.label.set_margin_bottom(4)

        action = "break" if is_break else "micro-pause"
        postpone_btn = Gtk.Button(label=f"Take {action} in {postpone_min} {UNIT_LABEL}")
        postpone_btn.connect("clicked", lambda *_: on_postpone())
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.set_margin_bottom(8)
        btn_box.pack_start(postpone_btn, False, False, 0)
        if is_break:
            skip_btn = Gtk.Button(label="Skip")
            skip_btn.connect("clicked", lambda *_: on_skip())
            btn_box.pack_start(skip_btn, False, False, 0)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.pack_start(self.label, False, False, 0)
        box.pack_start(btn_box, False, False, 0)
        self.add(box)

        self.show_all()
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        geo = monitor.get_geometry()
        w, h = self.get_size()
        self.move(geo.x + geo.width - w - 24, geo.y + geo.height - h - 48)
        self._animate_opacity(1.0, FADE_IN_MS)

    def set_text(self, big, small):
        base_pt = system_font_pt()
        small_pt = base_pt - 1
        big_pt = base_pt + 4
        self.label.set_markup(
            f'<span size="{int(big_pt * 1024)}" weight="bold">{big}</span>\n'
            f'<span size="{int(small_pt * 1024)}">{small}</span>'
        )

    def _animate_opacity(self, target, duration_ms, on_complete=None):
        steps = max(1, duration_ms // FADE_STEP_MS)
        start = Gtk.Widget.get_opacity(self)
        step = [0]

        def tick():
            step[0] += 1
            if step[0] >= steps:
                Gtk.Widget.set_opacity(self, target)
                if on_complete:
                    on_complete()
                return False
            Gtk.Widget.set_opacity(self, start + (target - start) * step[0] / steps)
            return True

        GLib.timeout_add(FADE_STEP_MS, tick)

    def dismiss(self):
        self._animate_opacity(0.0, FADE_OUT_MS, on_complete=self.destroy)


class FullscreenPause(Gtk.Window):
    def __init__(self, title, duration_sec, postpone_min, on_done, on_postpone, is_break):
        super().__init__()
        self.remaining = duration_sec
        self.on_done = on_done
        self.on_postpone = on_postpone
        self.is_break = is_break

        self.set_decorated(False)
        self.set_keep_above(True)
        self.stick()
        self.get_style_context().add_class("pause-window")

        title_label = Gtk.Label(label=title)
        title_label.get_style_context().add_class("title")
        self.countdown_label = Gtk.Label()
        self.countdown_label.get_style_context().add_class("countdown")
        self._update_countdown()

        action = "break" if is_break else "micro-pause"
        postpone_btn = Gtk.Button(label=f"Take {action} in {postpone_min} {UNIT_LABEL}")
        postpone_btn.connect("clicked", self._postpone)
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        btn_box.set_halign(Gtk.Align.CENTER)
        btn_box.pack_start(postpone_btn, False, False, 0)
        if is_break:
            skip_btn = Gtk.Button(label="Skip")
            skip_btn.connect("clicked", self._skip)
            btn_box.pack_start(skip_btn, False, False, 0)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        box.set_valign(Gtk.Align.CENTER)
        box.set_halign(Gtk.Align.CENTER)
        box.pack_start(title_label, False, False, 0)
        box.pack_start(self.countdown_label, False, False, 0)
        box.pack_start(btn_box, False, False, 0)
        self.add(box)

        self.connect("key-press-event", self._on_key)
        self.connect("delete-event", lambda *a: True)

        self.show_all()
        self.fullscreen()
        GLib.timeout_add_seconds(1, self._tick)

    def _update_countdown(self):
        if self.remaining >= 60:
            self.countdown_label.set_label(f"{self.remaining // 60} min")
        else:
            m, s = divmod(self.remaining, 60)
            self.countdown_label.set_label(f"{m:02d}:{s:02d}")

    def _tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.destroy()
            self.on_done()
            return False
        self._update_countdown()
        return True

    def _skip(self, *_):
        self.destroy()
        self.on_done()

    def _postpone(self, *_):
        self.destroy()
        self.on_postpone()

    def _on_key(self, widget, event):
        if event.keyval == Gdk.KEY_Escape and self.is_break:
            self._skip()


class BreakApp:
    def __init__(self, debug=False):
        self.cfg = dict(DEBUG_DEFAULTS) if debug else load_config()
        now = time.time()
        self.next_break = now + self.cfg["BREAK_INTERVAL_MIN"] * UNIT_SEC
        self.next_micro = now + self.cfg["MICRO_INTERVAL_MIN"] * UNIT_SEC
        self.break_stage = None   # None -> warn1 -> warn2 -> countdown
        self.micro_stage = None   # None -> countdown
        self.popups = {True: None, False: None}  # keyed by is_break
        self.active_window = None
        self.timers_disabled = False
        self.disabled_at = None
        self.paused_until = None
        self.pause_label = None

        self.indicator = AppIndicator3.Indicator.new(
            "regular-breaks",
            ICON_NAME,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator.set_icon_theme_path(ICON_DIR)
        self.indicator.set_icon_full(ICON_NAME, "Regular breaks")
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()
        self.break_item = Gtk.MenuItem(label="")
        self.break_item.set_sensitive(False)
        self.micro_item = Gtk.MenuItem(label="")
        self.micro_item.set_sensitive(False)
        self.paused_item = Gtk.MenuItem(label="")
        self.paused_item.set_sensitive(False)
        self.paused_item.hide()
        self.resume_item = Gtk.MenuItem(label="Resume timers")
        self.resume_item.connect("activate", self.on_reset)
        self.resume_item.hide()
        self.menu.append(self.break_item)
        self.menu.append(self.micro_item)
        self.menu.append(self.paused_item)
        self.menu.append(self.resume_item)
        self.menu.append(Gtk.SeparatorMenuItem())

        self.take_break_item = Gtk.MenuItem(label="Take Break Now")
        self.take_break_item.connect("activate", self.on_take_break_now)
        self.menu.append(self.take_break_item)

        self.take_micro_item = Gtk.MenuItem(label="Take Micro-pause Now")
        self.take_micro_item.connect("activate", self.on_take_micro_now)
        self.menu.append(self.take_micro_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        reset_item = Gtk.MenuItem(label="Reset timers")
        reset_item.connect("activate", self.on_reset)
        self.menu.append(reset_item)

        pause_item = Gtk.MenuItem(label="Pause timers")
        pause_submenu = Gtk.Menu()
        for label, minutes in (("30 min", 30), ("1 hour", 60), ("2 hours", 120)):
            entry = Gtk.MenuItem(label=label)
            entry.connect("activate", self.on_pause_timers, minutes, label)
            pause_submenu.append(entry)
        pause_item.set_submenu(pause_submenu)
        self.menu.append(pause_item)

        self.disable_item = Gtk.CheckMenuItem(label="Disable timers")
        self.disable_item.connect("toggled", self.on_toggle_disable)
        self.menu.append(self.disable_item)

        self.menu.append(Gtk.SeparatorMenuItem())
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        GLib.timeout_add_seconds(1, self.tick)

    def _dismiss_popup(self, is_break):
        popup = self.popups[is_break]
        if popup:
            popup.dismiss()
            self.popups[is_break] = None

    def _postpone_min(self, is_break):
        return self.cfg["POSTPONE_MIN"] if is_break else self.cfg["MICRO_POSTPONE_MIN"]

    def _open_popup(self, big, small, is_break, auto_hide_sec=None):
        self._dismiss_popup(is_break)
        popup = NotifyPopup(
            big, small, self._postpone_min(is_break),
            on_skip=lambda: self._pause_finished(is_break),
            on_postpone=lambda: self._pause_postponed(is_break),
            is_break=is_break,
        )
        self.popups[is_break] = popup
        if auto_hide_sec:
            GLib.timeout_add_seconds(auto_hide_sec, lambda: self._auto_hide(is_break, popup))

    def _auto_hide(self, is_break, popup):
        if self.popups[is_break] is popup:
            popup.dismiss()
            self.popups[is_break] = None
        return False

    def _start_pause(self, is_break):
        self._dismiss_popup(True)
        self._dismiss_popup(False)
        if is_break:
            duration = self.cfg["BREAK_DURATION_MIN"] * UNIT_SEC
            title = "Time for a break"
        else:
            duration = self.cfg["MICRO_DURATION_SEC"]
            title = "Micro-pause"
        self.active_window = FullscreenPause(
            title, duration, self._postpone_min(is_break),
            on_done=lambda: self._pause_finished(is_break),
            on_postpone=lambda: self._pause_postponed(is_break),
            is_break=is_break,
        )

    def _pause_finished(self, is_break):
        self.active_window = None
        self._dismiss_popup(is_break)
        now = time.time()
        if is_break:
            self.next_break = now + self.cfg["BREAK_INTERVAL_MIN"] * UNIT_SEC
            self.next_micro = now + self.cfg["MICRO_INTERVAL_MIN"] * UNIT_SEC
            self.break_stage = None
            self.micro_stage = None
            self._dismiss_popup(False)
        else:
            self.next_micro = now + self.cfg["MICRO_INTERVAL_MIN"] * UNIT_SEC
            self.micro_stage = None

    def _pause_postponed(self, is_break):
        self.active_window = None
        self._dismiss_popup(is_break)
        now = time.time()
        postpone_sec = self._postpone_min(is_break) * UNIT_SEC
        if is_break:
            self.next_break = now + postpone_sec
            self.break_stage = None
        else:
            self.next_micro = now + postpone_sec
            self.micro_stage = None

    @staticmethod
    def _fmt(seconds):
        seconds = max(0, int(seconds))
        m, s = divmod(seconds, 60)
        return f"{m} min" if seconds > 180 else f"{m} min {s:02d}s"

    def _update_status_label(self, now):
        break_dur = self.cfg["BREAK_DURATION_MIN"]
        micro_dur = self.cfg["MICRO_DURATION_SEC"]

        if self.paused_until is not None:
            continues = self._fmt(self.paused_until - now)
            text = f"⏸ Paused ({self.pause_label}) — timers resume in {continues}"
            self.break_item.hide()
            self.micro_item.hide()
            self.paused_item.set_label(text)
            self.paused_item.show()
            self.resume_item.show()
            self.indicator.set_title(text)
            return

        self.paused_item.hide()
        self.resume_item.hide()
        self.break_item.show()
        self.micro_item.show()
        if self.timers_disabled:
            self.break_item.set_label(f"Next {break_dur} min break: disabled")
            self.micro_item.set_label(f"Next {micro_dur}s micro-pause: disabled")
            self.indicator.set_title("Timers disabled")
            return
        break_text = f"Next {break_dur} min break in {self._fmt(self.next_break - now)}"
        micro_text = f"Next {micro_dur}s micro-pause in {self._fmt(self.next_micro - now)}"
        self.break_item.set_label(break_text)
        self.micro_item.set_label(micro_text)
        self.indicator.set_title(f"{break_text}\n{micro_text}")

    def on_reset(self, *_):
        now = time.time()
        self.next_break = now + self.cfg["BREAK_INTERVAL_MIN"] * UNIT_SEC
        self.next_micro = now + self.cfg["MICRO_INTERVAL_MIN"] * UNIT_SEC
        self.break_stage = None
        self.micro_stage = None
        self.paused_until = None
        self.pause_label = None
        self._dismiss_popup(True)
        self._dismiss_popup(False)
        self._update_status_label(now)

    def on_take_break_now(self, *_):
        if self.active_window is None:
            self._start_pause(True)

    def on_take_micro_now(self, *_):
        if self.active_window is None:
            self._start_pause(False)

    def on_toggle_disable(self, checkmenuitem):
        self.timers_disabled = checkmenuitem.get_active()
        now = time.time()
        if self.timers_disabled:
            self.disabled_at = now
            self.paused_until = None
            self.pause_label = None
            self._dismiss_popup(True)
            self._dismiss_popup(False)
        elif self.disabled_at is not None:
            elapsed = now - self.disabled_at
            self.next_break += elapsed
            self.next_micro += elapsed
            self.disabled_at = None

    def on_pause_timers(self, _item, minutes, label):
        now = time.time()
        delay = minutes * 60
        self.paused_until = now + delay
        self.pause_label = label
        self.next_break = self.paused_until + self.cfg["BREAK_INTERVAL_MIN"] * UNIT_SEC
        self.next_micro = self.paused_until + self.cfg["MICRO_INTERVAL_MIN"] * UNIT_SEC
        self.break_stage = None
        self.micro_stage = None
        self._dismiss_popup(True)
        self._dismiss_popup(False)

    def _process_break(self, now):
        remaining = self.next_break - now
        dur = self.cfg["BREAK_DURATION_MIN"]
        if remaining <= 0:
            self._start_pause(True)
            return True

        cd_sec = self.cfg["BREAK_COUNTDOWN_SEC"]
        warn2_sec = self.cfg["BREAK_WARN_2_MIN"] * UNIT_SEC
        warn1_sec = self.cfg["BREAK_WARN_1_MIN"] * UNIT_SEC

        small = f"until {dur} min break"
        if remaining <= cd_sec:
            big = f"{int(remaining) + 1}s"
            if self.break_stage != "countdown":
                self._open_popup(big, small, True)
                self.break_stage = "countdown"
            else:
                self.popups[True].set_text(big, small)
        elif remaining <= warn2_sec and self.break_stage not in ("warn2", "countdown"):
            self._open_popup(f"{self.cfg['BREAK_WARN_2_MIN']} min", small, True, auto_hide_sec=10)
            self.break_stage = "warn2"
        elif remaining <= warn1_sec and self.break_stage is None:
            self._open_popup(f"{self.cfg['BREAK_WARN_1_MIN']} min", small, True, auto_hide_sec=10)
            self.break_stage = "warn1"
        return False

    def _process_micro(self, now):
        remaining = self.next_micro - now
        dur = self.cfg["MICRO_DURATION_SEC"]
        if remaining <= 0:
            self._start_pause(False)
            return

        cd_sec = self.cfg["MICRO_COUNTDOWN_SEC"]
        if remaining <= cd_sec:
            big = f"{int(remaining) + 1}s"
            small = f"until {dur}s micro-pause"
            if self.micro_stage != "countdown":
                self._open_popup(big, small, False)
                self.micro_stage = "countdown"
            else:
                self.popups[False].set_text(big, small)

    def tick(self):
        if self.active_window is not None:
            return True
        now = time.time()
        if self.paused_until is not None and now >= self.paused_until:
            self.paused_until = None
            self.pause_label = None
        self._update_status_label(now)
        if self.timers_disabled:
            return True

        if self._process_break(now):
            return True
        self._process_micro(now)
        return True

    def quit(self, *_):
        Gtk.main_quit()


def _debug_unit(value):
    v = int(value)
    if not 1 <= v <= 60:
        raise argparse.ArgumentTypeError("must be between 1 and 60")
    return v


def main():
    global UNIT_SEC, UNIT_LABEL
    parser = argparse.ArgumentParser(description="Regular breaks tray app")
    parser.add_argument(
        "-d", "--debug", nargs="?", type=_debug_unit, const=1, default=None,
        metavar="UNIT_SEC",
        help="debug mode: use in-script DEBUG_ constants; optional UNIT_SEC (1-60, "
             "default 1) sets how many seconds count as one minute",
    )
    args = parser.parse_args()
    if args.debug is not None:
        UNIT_SEC, UNIT_LABEL = args.debug, "s"
        print(f"Debug mode: using DEBUG_DEFAULTS, 1 min == {UNIT_SEC}s")

    provider = Gtk.CssProvider()
    provider.load_from_data(build_css())
    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    BreakApp(debug=args.debug is not None)
    Gtk.main()


if __name__ == "__main__":
    main()
