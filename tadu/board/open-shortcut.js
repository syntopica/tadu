import { DEFAULT_FILTERS } from "./default-filters.js";
import { setView } from "./set-view.js";
import { store } from "./store.js";

// Show All work with only a shortcut's filters, keeping the scope and
// whether cancelled items show.
export function openShortcut(filters) {
  store.filters = { ...DEFAULT_FILTERS, showCancelled: store.filters.showCancelled, ...filters };
  setView("all");
}
