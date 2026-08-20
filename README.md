# Regular Breaks

A GTK3 tray app for Linux that reminds you to take regular breaks and
short micro-pauses, with a countdown, prepare notices, and a fullscreen
break/pause overlay you can skip or postpone.

## Requirements

- Linux with a tray/AppIndicator-capable desktop (GNOME needs an
  AppIndicator extension; KDE, XFCE, Cinnamon etc. support it natively)
- Python 3
- PyGObject and the Ayatana AppIndicator3 introspection bindings

On Debian/Ubuntu:

```
sudo apt install python3-gi gir1.2-ayatanaappindicator3-0.1
```

## Install

```
python3 install.py
```

This checks that the dependencies above are present, makes
`regular_breaks.py` executable, and adds a "Regular Breaks" entry to
your application menu. It does not enable autostart — use the tray
icon's **Start on login** menu item for that (see below).

## Uninstall

```
python3 uninstall.py
```

Removes the application menu entry and any autostart entry created via
"Start on login". `config.txt` and `icons/` are left in place.

## Usage

Run directly, or launch "Regular Breaks" from your application menu:

```
python3 regular_breaks.py
```

A coffee-cup icon appears in the tray. Its menu shows the time until
the next break and micro-pause, and offers:

- **Take Break Now** / **Take Micro-pause Now** — trigger one immediately
- **Reset timers** — restart both countdowns from their full interval
- **Pause timers** — suspend both timers for 30 min / 1 hour / 2 hours
- **Disable break timer** / **Disable micro-pause timer** — turn either
  reminder off independently until unchecked
- **Start on login** — add/remove a `~/.config/autostart` entry so the
  app launches automatically when you log in
- **Quit**

As a break or micro-pause approaches, a small notification appears in
the corner with a final countdown. When it fires, a fullscreen overlay
takes over the screen; **Skip** or **Postpone** dismiss it (Escape
also skips a break).

## Configuration

Settings live in `config.txt`, next to the script — a flat
`KEY=value` file, created with defaults on first run if it doesn't
exist. Unknown or invalid lines are ignored.

| Key | Default | Meaning |
|---|---|---|
| `BREAK_INTERVAL_MIN` | 30 | Minutes between breaks |
| `BREAK_DURATION_MIN` | 5 | Length of a break |
| `MICRO_INTERVAL_MIN` | 10 | Minutes between micro-pauses |
| `MICRO_DURATION_SEC` | 20 | Length of a micro-pause |
| `BREAK_FIRST_PREPARE_NOTICE_MIN` | 2 | First break prepare notice, minutes before |
| `BREAK_SECOND_PREPARE_NOTICE_MIN` | 1 | Second break prepare notice, minutes before |
| `BREAK_COUNTDOWN_SEC` | 30 | Final break countdown popup, seconds before |
| `MICRO_COUNTDOWN_SEC` | 10 | Final micro-pause countdown popup, seconds before |
| `POSTPONE_MIN` | 2 | Snooze length when postponing a break |
| `MICRO_POSTPONE_MIN` | 1 | Snooze length when postponing a micro-pause |

## Debug mode

```
python3 regular_breaks.py -d [UNIT_SEC]
```

Runs with a separate set of short, in-script defaults and treats every
`_MIN` value as seconds instead of minutes, so a full cycle finishes
in well under a minute — useful for testing without editing
`config.txt`. `UNIT_SEC` (1–60, default 1) sets how many real seconds
count as one "minute" in debug mode.
