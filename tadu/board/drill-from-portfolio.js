import { DEFAULT_FILTERS } from "./default-filters.js";
import { setView } from "./set-view.js";
import { setWhere } from "./set-where.js";
import { store } from "./store.js";

// Open a portfolio row's items: its scope (`where`, or the current one when
// null) with only its `filter` (a relation's organization and role), in
// `view`, narrowed to `column` when one is given. What it replaces is
// remembered so that going back to Portfolio restores it; the scope also
// joins the recent ones.
export function drillFromPortfolio(where, filter, view, column) {
  const before = {
    filters: store.filters,
    text: store.text,
    scope: store.scope,
    where: store.where,
  };
  setWhere(where ?? store.where);
  store.beforeDrill = before;
  store.filters = { ...DEFAULT_FILTERS, showCancelled: store.filters.showCancelled, ...filter };
  store.text = "";
  document.getElementById("search").value = "";
  store.scope = "all";
  setView(view, column);
}
