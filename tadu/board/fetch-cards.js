// GET the card data with the per-run token; throws an Error carrying the
// HTTP status (0 when the server could not be reached) and its message.
export async function fetchCards(token) {
  const response = await fetch("/api/cards", {
    cache: "no-store",
    headers: { "X-Tadu-Token": token },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(body.error ?? `HTTP ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return body;
}
