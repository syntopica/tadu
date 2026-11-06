import { boardToken } from "./board-token.js";
import { fetchCards } from "./fetch-cards.js";
import { loadErrorText } from "./load-error-text.js";
import { loadSavedViews } from "./load-saved-views.js";
import { requestRender } from "./request-render.js";
import { searchText } from "./search-text.js";
import { store } from "./store.js";

// Fetch the cards and index them once. A failed reload keeps the old data
// on screen and reports the error; a response that is not the latest
// request's is dropped.
export async function loadBoard() {
  const token = boardToken();
  if (!token) {
    store.error = "No token: open the URL that `tadu board` printed.";
    requestRender();
    return;
  }
  store.requests += 1;
  const request = store.requests;
  store.loading = true;
  requestRender();
  try {
    const payload = await fetchCards(token);
    if (request !== store.requests) {
      return;
    }
    if (payload.workspace_id !== store.payload?.workspace_id) {
      store.saved = loadSavedViews(payload.workspace_id);
    }
    store.payload = payload;
    store.cards = payload.cards;
    store.texts = new Map(payload.cards.map((card) => [card, searchText(card)]));
    store.byKey = new Map(payload.cards.map((card) => [card.key, card]));
    store.error = "";
  } catch (error) {
    if (request === store.requests) {
      store.error = loadErrorText(error, store.payload !== null);
    }
  } finally {
    if (request === store.requests) {
      store.loading = false;
      requestRender();
    }
  }
}
