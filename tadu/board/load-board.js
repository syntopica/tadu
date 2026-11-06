import { adoptPayload } from "./adopt-payload.js";
import { boardToken } from "./board-token.js";
import { fetchCards } from "./fetch-cards.js";
import { loadErrorText } from "./load-error-text.js";
import { requestRender } from "./request-render.js";
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
    adoptPayload(store, payload);
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
