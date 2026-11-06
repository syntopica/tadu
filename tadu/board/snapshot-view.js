import { store } from "./store.js";

// What a saved view remembers of the current page, its scope included.
export function snapshotView(name) {
  return {
    name,
    view: store.view,
    text: store.text,
    filters: { ...store.filters },
    where: { ...store.where },
    scope: store.scope,
    group: store.group,
    sort: store.sort,
  };
}
