import { adoptPayload } from "./adopt-payload.js";
import { boardToken } from "./board-token.js";
import { fetchCards } from "./fetch-cards.js";
import { leaveSignedOut } from "./leave-signed-out.js";
import { loadErrorText } from "./load-error-text.js";
import { requestRender } from "./request-render.js";
import { signedOut } from "./signed-out.js";
import { store } from "./store.js";

// Fetch the cards and index them once. An ended session leaves for the
// sign-in page with nothing left on screen; any other failed reload keeps the
// old data on screen and reports the error; a response that is not the latest
// request's is dropped. Without a token the request still goes out: a board
// that signs in with GitHub knows the person by their session, and a token
// board's refusal reads as before, "No token: open the URL ...".
export async function loadBoard() {
  const token = boardToken();
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
    if (request === store.requests && signedOut(error)) {
      leaveSignedOut(store);
    } else if (request === store.requests) {
      store.error = loadErrorText(error, store.payload !== null, !token);
    }
  } finally {
    if (request === store.requests && !store.left) {
      store.loading = false;
      requestRender();
    }
  }
}
