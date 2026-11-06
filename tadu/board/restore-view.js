import { DEFAULT_FILTERS } from "./default-filters.js";
import { requestRender } from "./request-render.js";
import { store } from "./store.js";

// Put a saved view back on the page.
export function restoreView(saved) {
  store.view = saved.view ?? "board";
  store.text = saved.text ?? "";
  store.filters = { ...DEFAULT_FILTERS, ...saved.filters };
  store.scope = saved.scope ?? "all";
  store.group = saved.group ?? "state";
  store.sort = saved.sort ?? "priority";
  store.collapsed = new Set();
  store.navOpen = false;
  document.getElementById("search").value = store.text;
  requestRender();
}
