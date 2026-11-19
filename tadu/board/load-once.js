import { failureText } from "./failure-text.js";
import { requestRender } from "./request-render.js";

// Fetch once for `key` into `state`, a view's part of the store: the
// result goes to `state.payload`, a failure to `state.error` (see
// failureText, `failed` saying what failed), and `state.loadedFor` says
// which key they answer. A result no longer wanted (`state.wanted` moved on)
// is dropped. The page renders again when it is in.
export async function loadOnce(state, key, fetchIt, failed) {
  state.wanted = key;
  state.loading = true;
  try {
    const payload = await fetchIt();
    if (state.wanted === key) {
      state.payload = payload;
      state.error = "";
    }
  } catch (error) {
    if (state.wanted === key) {
      state.error = failureText(error, failed);
    }
  } finally {
    if (state.wanted === key) {
      state.loading = false;
      state.loadedFor = key;
      requestRender();
    }
  }
}
