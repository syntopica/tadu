import { BOARD_CHECK_TIMING } from "./board-check-timing.js";

// When to check again after a passed check: as usual, but no later than the
// moment the session's warning is due, nor just after the session's end, so
// the warning shows on time and an ended session leaves at once.
export function nextCheckMs(answer) {
  const every = BOARD_CHECK_TIMING.everyMs;
  if (answer.remaining === null) {
    return every;
  }
  const untilWarning = (answer.remaining - answer.warn) * 1000;
  return Math.min(every, untilWarning > 0 ? untilWarning : answer.remaining * 1000 + 1000);
}
