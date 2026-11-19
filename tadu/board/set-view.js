import { requestRender } from "./request-render.js";
import { restoreDrill } from "./restore-drill.js";
import { setRule } from "./set-rule.js";
import { store } from "./store.js";

// Switch view, starting from its own grouping and sort: Done by closing
// day, Blocked by project (by repository without projects), the others by
// state and priority. A `column` narrows it to that state (a State rule);
// none drops the State rule. Returning to Portfolio undoes the filters its
// last drill-down set.
export function setView(view, column = "") {
  const [group, sort] = {
    done: ["day", "closed"],
    blocked: [store.index?.projects.size === 0 ? "repository" : "project", "priority"],
  }[view] ?? ["state", "priority"];
  if (view === "portfolio") {
    restoreDrill(store);
    document.getElementById("search").value = store.text;
  }
  store.view = view;
  const state = { field: "state", op: "any", values: column === "" ? [] : [column] };
  store.filters = { ...store.filters, rules: setRule(store.filters.rules, state) };
  store.group = group;
  store.sort = sort;
  store.navOpen = false;
  store.collapsed = new Set();
  window.scrollTo(0, 0);
  requestRender();
}
