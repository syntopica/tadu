// Ask the board whether the page may still show what it shows; `active` (a
// POST) also tells it the person acted on the page since the last check, which
// counts as using the board and pushes the session's end back. The answer's
// `state` is "ok" (with, for a GitHub session, the seconds it has `remaining`
// unused and how long before its end to `warn`), "signed-out" when the board
// says the session ended (or, on a token board, refuses the token: it
// restarted), or "down" when it cannot be reached or answers anything else,
// such as a proxy's 502.
export async function fetchCheck(token, active = false) {
  try {
    const response = await fetch("api/session", {
      method: active ? "POST" : "GET",
      cache: "no-store",
      headers: token ? { "X-Tadu-Token": token } : {},
    });
    const body = await response.json().catch(() => ({}));
    if (response.ok) {
      return { state: "ok", remaining: body.remaining ?? null, warn: body.warn ?? 0 };
    }
    const ended = response.status === 401 && body.error === "signed out";
    return { state: ended || (response.status === 403 && token) ? "signed-out" : "down" };
  } catch {
    return { state: "down" };
  }
}
