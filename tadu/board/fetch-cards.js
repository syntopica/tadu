// GET the card data, relative to the page (a board served in a subfolder asks
// its own), with the per-run token when the page has one (a board that signs
// in with GitHub needs none: the browser sends the session);
// throws an Error carrying the HTTP status (0 when the server could not be
// reached) and its message.
export async function fetchCards(token) {
  const response = await fetch("api/cards", {
    cache: "no-store",
    headers: token ? { "X-Tadu-Token": token } : {},
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.error ?? `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}
