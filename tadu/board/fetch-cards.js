// GET the card data with the per-run token; throws with the server's message.
export async function fetchCards(token) {
  const response = await fetch("/api/cards", {
    cache: "no-store",
    headers: { "X-Tadu-Token": token },
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.error ?? `HTTP ${response.status}`);
  }
  return body;
}
