import { pushRecent } from "./push-recent.js";
import { requestRender } from "./request-render.js";
import { storageKey } from "./storage-key.js";
import { store } from "./store.js";
import { writeStored } from "./write-stored.js";

// Choose the places every view shows (none: the whole workspace) and, when
// `remember` (a final choice, not a tick on the way to one), record them
// among the recent scopes. A pending portfolio drill-down is forgotten:
// the person has picked a scope of their own.
export function setPlaces(places, remember = true) {
  store.places = places.map(({ company, project, repository }) => ({ company, project, repository }));
  if (remember) {
    store.recent = pushRecent(store.recent, store.places);
    writeStored(storageKey("recent", store.payload.workspace_id), store.recent);
  }
  store.beforeDrill = null;
  store.collapsed = new Set();
  requestRender();
}
