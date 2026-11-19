import { ACTIVITY_EVENTS } from "./activity-events.js";
import { BOARD_CHECK_TIMING } from "./board-check-timing.js";
import { boardToken } from "./board-token.js";
import { fetchCheck } from "./fetch-check.js";
import { leaveSignedOut } from "./leave-signed-out.js";
import { nextCheckMs } from "./next-check-ms.js";
import { showSessionWarning } from "./show-session-warning.js";
import { showUnreachable } from "./show-unreachable.js";

// Keep checking, while the page is visible, that it may show what it shows:
// an ended session (or refused token) leaves for the sign-in page; a board
// that stops answering clears the page until it answers again, then the page
// reloads. A hidden page does not check, and checks at once when shown again.
// A check keeps a session alive only when the person acted on the page since
// the last one (ACTIVITY_EVENTS): it then says so, and the end moves on; a
// page left alone is not activity. A session the idle timeout is about to end
// is warned about; any activity then, or Stay signed in, answers at once.
export function watchBoard(store) {
  const watch = { failures: 0, down: false, timer: 0, busy: false, active: false, session: false };
  const check = async () => {
    if (watch.busy || document.visibilityState === "hidden") {
      return;
    }
    watch.busy = true;
    window.clearTimeout(watch.timer);
    const active = watch.active && watch.session;
    watch.active &&= !active;
    const answer = await fetchCheck(boardToken(), active);
    watch.busy = false;
    watch.session ||= answer.state === "ok" && answer.remaining !== null;
    if (answer.state === "signed-out") {
      leaveSignedOut(store);
      return;
    }
    if (answer.state === "ok" && watch.down) {
      window.location.reload();
      return;
    }
    watch.failures = answer.state === "ok" ? 0 : watch.failures + 1;
    if (!watch.down) {
      showSessionWarning(answer.state === "ok" ? answer : null);
    }
    if (!watch.down && watch.failures >= BOARD_CHECK_TIMING.downAfter) {
      watch.down = true;
      showUnreachable(store);
    }
    const wait = answer.state === "ok" ? nextCheckMs(answer) : BOARD_CHECK_TIMING.retryMs;
    // Activity while this check was out answers a warning at once, not a check later.
    const answerNow = watch.active && document.getElementById("session-warning")?.hidden === false;
    watch.timer = window.setTimeout(check, answerNow ? 0 : wait);
  };
  document.addEventListener("visibilitychange", check);
  window.addEventListener("online", check);
  const activity = () => {
    watch.active = true;
    if (document.getElementById("session-warning")?.hidden === false) {
      check();
    }
  };
  for (const name of ACTIVITY_EVENTS) {
    window.addEventListener(name, activity, { capture: true, passive: true });
  }
  document.getElementById("stay-signed-in").addEventListener("click", activity);
  watch.timer = window.setTimeout(check, BOARD_CHECK_TIMING.everyMs);
  return check;
}
