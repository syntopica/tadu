import { requestRender } from "./request-render.js";
import { store } from "./store.js";

// Switch view, starting from its own grouping and sort: Done by closing
// day, Blocked by project, the others by state and priority.
export function setView(view, column = "") {
  const [group, sort] = { done: ["day", "closed"], blocked: ["project", "priority"] }[view] ?? [
    "state",
    "priority",
  ];
  store.view = view;
  store.filters = { ...store.filters, column };
  store.group = group;
  store.sort = sort;
  store.navOpen = false;
  store.collapsed = new Set();
  window.scrollTo(0, 0);
  requestRender();
}
