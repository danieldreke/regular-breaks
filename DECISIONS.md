# Decisions

## Micro-pauses do not overlap a break

A micro-pause is skipped when the time left until the next break is shorter than `MICRO_INTERVAL`. An equal gap still runs, so with a 30-minute break and a 10-minute micro-pause the micro-pauses at 10 and 20 minutes still happen, and the one that would land on the break does not.

Finishing a break restarts both timers from that moment. A disabled break timer does not suppress micro-pauses.

Implemented in `regular_breaks.py`: `_process_micro` returns early on that gap, and `_pause_finished` resets `next_break` and `next_micro` when a break ends.

## A long enough screen lock counts as the pause

On unlock, the app reads how long the logind session stayed locked (`LockedHint`). A lock of at least `MICRO_DURATION` restarts the micro-pause timer for a full `MICRO_INTERVAL`. A lock of at least `BREAK_DURATION` restarts the break timer for a full `BREAK_INTERVAL`. Each restart is measured from unlock, and that timer's notice is cleared.

Implemented in `regular_breaks.py`: `_watch_screen_lock` and `_on_screen_locked`.
