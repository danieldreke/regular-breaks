# Decisions

## Micro-pauses do not overlap a break

A micro-pause is skipped when the time left until the next break is shorter than `MICRO_INTERVAL`. An equal gap still runs, so with a 30-minute break and a 10-minute micro-pause the micro-pauses at 10 and 20 minutes still happen, and the one that would land on the break does not.

Finishing a break restarts both timers from that moment. A disabled break timer does not suppress micro-pauses.

While that skip is active, the tray says the next micro-pause is "after break" and does not count it down. A micro-pause countdown already open is dismissed.

Implemented in `regular_breaks.py`: `_process_micro` returns early on that gap, `_update_status_label` shows "after break", and `_pause_finished` resets `next_break` and `next_micro` when a break ends.

## A screen lock resets the micro-pause timer

Every lock restarts the micro-pause timer for a full `MICRO_INTERVAL`, and every unlock does that again. Neither restart depends on how long the screen stayed locked. The break timer still restarts on unlock only when the lock lasted at least `BREAK_DURATION`. Each restart is measured from that event, and that timer's notice is cleared.

A break or micro-pause does not start while the screen is locked. `tick()` updates the tray label and returns while `locked_at` is set. "Take Break Now" and "Take Micro-pause Now" still start immediately.

Sleep and wake each restart both timers for a full interval. logind `PrepareForSleep` sets `asleep` before sleep and clears it on wake. If `tick()` runs first after resume, `asleep` is still set, so that tick restarts both timers and does not start a pause.

Implemented in `regular_breaks.py`: `_on_screen_locked`, `_reset_timer`, `_on_prepare_for_sleep`, and the `locked_at` and `asleep` returns in `tick()`.
