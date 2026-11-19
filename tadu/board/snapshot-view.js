import { store } from "./store.js";

// What a saved view remembers of the current page, its scope included.
export function snapshotView(name) {
  return {
    name,
    view: store.view,
    text: store.text,
    filters: { ...store.filters },
    places: store.places.map((place) => ({ ...place })),
    scope: store.scope,
    group: store.group,
    sort: store.sort,
  };
}
