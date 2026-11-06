import { cleanSavedView } from "./clean-saved-view.js";
import { cleanWhere } from "./clean-where.js";
import { existingFilters } from "./existing-filters.js";
import { requestRender } from "./request-render.js";
import { store } from "./store.js";

// Put a saved view back on the page, its scope included, keeping only
// filter and scope values the current workspace still offers.
export function restoreView(saved) {
  const view = cleanSavedView(saved);
  if (view === null) {
    return;
  }
  store.view = view.view;
  store.text = view.text;
  store.filters = existingFilters(view.filters, store.cards, store.payload?.columns ?? []);
  store.where = cleanWhere(view.where, store.index);
  store.scope = view.scope;
  store.group = view.group;
  store.sort = view.sort;
  store.collapsed = new Set();
  store.navOpen = false;
  document.getElementById("search").value = store.text;
  requestRender();
}
