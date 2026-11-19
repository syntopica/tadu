import { fetchChanges } from "./fetch-changes.js";
import { loadOnce } from "./load-once.js";

// Fetch the changes of the chosen days once for `key` (the days and the
// board's load they belong to), as loadOnce does; a failure is kept as the
// view's error until the days change or the board reloads.
export async function loadChanges(store, key) {
  const state = store.changes;
  await loadOnce(
    state,
    key,
    () => fetchChanges(state.since, state.until, store.payload.today),
    "Changes unavailable",
  );
}
