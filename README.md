# Regular Breaks

![Claude](https://img.shields.io/badge/Built_With-Claude-D97757?style=flat&logo=claude&logoColor=D97757) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

The quickest way — no `git` required. Downloads the repo into
`./regular-breaks` and installs it in one step:

```
curl -fsSL https://raw.githubusercontent.com/danieldreke/regular-breaks/main/download.py | python3 - --install
```

Leave off `--install` to just download the files without installing:

```
curl -fsSL https://raw.githubusercontent.com/danieldreke/regular-breaks/main/download.py | python3 -
```

If you already have the repo locally (e.g. via `git clone`), install
directly instead:

```
python3 install.py
```

Either way, install checks that the dependencies above are present, makes
`regular_breaks.py` executable, and adds a "Regular Breaks" entry to
your application menu. It does not enable autostart — use the tray
icon's **Start on login** menu item for that (see below).

## Update

Re-downloads into an existing `--dir` instead of refusing to touch it,
overwriting the app's own files with the latest version:

```
curl -fsSL https://raw.githubusercontent.com/danieldreke/regular-breaks/main/download.py | python3 - --update --install
```

`config.txt` isn't part of the repository, so your settings are left alone.

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

Values are durations written as a combination of `h`/`m`/`s`, in that
order — e.g. `3m`, `10s`, `1h30m`, `20m10s`. At least one unit is
required; bare numbers aren't valid.

| Key | Default | Meaning |
|---|---|---|
| `BREAK_INTERVAL` | `30m` | Time between breaks |
| `BREAK_DURATION` | `5m` | Length of a break |
| `MICRO_INTERVAL` | `10m` | Time between micro-pauses |
| `MICRO_DURATION` | `20s` | Length of a micro-pause |
| `BREAK_FIRST_PREPARE_NOTICE` | `2m` | First break prepare notice, time before |
| `BREAK_SECOND_PREPARE_NOTICE` | `1m` | Second break prepare notice, time before |
| `BREAK_COUNTDOWN` | `30s` | Final break countdown popup, time before |
| `MICRO_COUNTDOWN` | `10s` | Final micro-pause countdown popup, time before |
| `POSTPONE` | `2m` | Snooze length when postponing a break |
| `MICRO_POSTPONE` | `1m` | Snooze length when postponing a micro-pause |

## Debug mode

```
python3 regular_breaks.py -d [SPEED]
```

Runs with a separate set of short, in-script durations instead of
`config.txt`, so a full cycle finishes in well under a minute — useful
for testing without editing `config.txt`. `SPEED` (1–60, default 1)
multiplies every debug duration by that many real seconds, letting you
slow debug mode down instead of always running at full speed.
