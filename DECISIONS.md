# Decisions

## Micro-pauses do not overlap a break

A micro-pause is skipped when the time left until the next break is shorter than `MICRO_INTERVAL`. An equal gap still runs, so with a 30-minute break and a 10-minute micro-pause the micro-pauses at 10 and 20 minutes still happen, and the one that would land on the break does not.

Finishing a break restarts both timers from that moment. A disabled break timer does not suppress micro-pauses.

Implemented in `regular_breaks.py`: `_process_micro` returns early on that gap, and `_pause_finished` resets `next_break` and `next_micro` when a break ends.
