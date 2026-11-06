import { boardToken } from "./board-token.js";
import { fetchCards } from "./fetch-cards.js";
import { requestRender } from "./request-render.js";
import { searchText } from "./search-text.js";
import { store } from "./store.js";

// Fetch the cards and index them once; a failed reload keeps the old data
// on screen and reports the error.
export async function loadBoard() {
  const token = boardToken();
  if (!token) {
    store.error = "No token: open the URL that `tadu board` printed.";
    requestRender();
    return;
  }
  store.loading = true;
  requestRender();
  try {
    const payload = await fetchCards(token);
    store.payload = payload;
    store.cards = payload.cards;
    store.texts = new Map(payload.cards.map((card) => [card, searchText(card)]));
    store.byKey = new Map(payload.cards.map((card) => [card.key, card]));
    store.error = "";
  } catch (error) {
    store.error = `Reload failed: ${error.message}`;
  } finally {
    store.loading = false;
    requestRender();
  }
}
