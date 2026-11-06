import { store } from "./store.js";

// What a saved view remembers of the current page.
export function snapshotView(name) {
  return {
    name,
    view: store.view,
    text: store.text,
    filters: { ...store.filters },
    scope: store.scope,
    group: store.group,
    sort: store.sort,
  };
}
