// Warn that the idle timeout ends the session soon, counting down each second,
// when a passed check says it is within its warning time; hide the warning
// otherwise (the session was used again, here or in another tab, or ended).
export function showSessionWarning(answer) {
  const banner = document.getElementById("session-warning");
  window.clearInterval(showSessionWarning.ticker);
  const left = answer?.remaining ?? null;
  if (left === null || left > answer.warn) {
    banner.hidden = true;
    return;
  }
  const end = Date.now() + left * 1000;
  const tick = () => {
    const text = document.getElementById("session-warning-text");
    if (!text) {
      window.clearInterval(showSessionWarning.ticker); // the page was emptied
      return;
    }
    const seconds = Math.max(0, Math.ceil((end - Date.now()) / 1000));
    const clock = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
    text.textContent = `You will be signed out in ${clock} for inactivity.`;
  };
  tick();
  banner.hidden = false;
  showSessionWarning.ticker = window.setInterval(tick, 1000);
}
