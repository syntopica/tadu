import { applyFilter } from "./apply-filter.js";
import { store } from "./store.js";

// Open a portfolio row's items, remembering the filters, search and scope it
// replaces so that going back to Portfolio restores them.
export function drillFromPortfolio(filter, view, column) {
  store.beforeDrill = {
    filters: store.filters,
    text: store.text,
    scope: store.scope,
  };
  applyFilter(filter, view, column);
}
