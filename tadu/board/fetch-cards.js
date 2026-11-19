import { responseBody } from "./response-body.js";

// GET the card data relative to the page (a board served in a subfolder asks
// its own), closed items `doneDays` back (the server's --done-days when
// null), with the per-run token when the page has one (a board that signs in
// with GitHub needs none: the browser sends the session); throws as
// responseBody does.
export async function fetchCards(token, doneDays = null) {
  const query = doneDays === null ? "" : `?${new URLSearchParams({ done_days: doneDays })}`;
  const response = await fetch(`api/cards${query}`, {
    cache: "no-store",
    headers: token ? { "X-Tadu-Token": token } : {},
  });
  return responseBody(response);
}
