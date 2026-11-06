import { DEFAULT_FILTERS } from "./default-filters.js";
import { setView } from "./set-view.js";
import { store } from "./store.js";

// Replace the filters with `filter` (keeping the cancelled toggle) and show
// `view`, narrowed to `column` when one is given.
export function applyFilter(filter, view, column = "") {
  store.filters = { ...DEFAULT_FILTERS, showCancelled: store.filters.showCancelled, ...filter };
  store.text = "";
  store.scope = "all";
  setView(view, column);
}
