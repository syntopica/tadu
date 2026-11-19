import { responseBody } from "./response-body.js";

// GET the card data with the per-run token, closed items `doneDays` back
// (the server's --done-days when null); throws as responseBody does.
export async function fetchCards(token, doneDays = null) {
  const query = doneDays === null ? "" : `?${new URLSearchParams({ done_days: doneDays })}`;
  const response = await fetch(`/api/cards${query}`, {
    cache: "no-store",
    headers: { "X-Tadu-Token": token },
  });
  return responseBody(response);
}
