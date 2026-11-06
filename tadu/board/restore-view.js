import { cleanSavedView } from "./clean-saved-view.js";
import { existingFilters } from "./existing-filters.js";
import { requestRender } from "./request-render.js";
import { store } from "./store.js";

// Put a saved view back on the page, keeping only filter values the current
// data still offers.
export function restoreView(saved) {
  const view = cleanSavedView(saved);
  if (view === null) {
    return;
  }
  store.view = view.view;
  store.text = view.text;
  store.filters = existingFilters(view.filters, store.cards, store.payload?.columns ?? []);
  store.scope = view.scope;
  store.group = view.group;
  store.sort = view.sort;
  store.collapsed = new Set();
  store.navOpen = false;
  document.getElementById("search").value = store.text;
  requestRender();
}
