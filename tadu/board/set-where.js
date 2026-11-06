import { pushRecent } from "./push-recent.js";
import { requestRender } from "./request-render.js";
import { storageKey } from "./storage-key.js";
import { store } from "./store.js";
import { writeStored } from "./write-stored.js";

// Choose the company, project and repository every view shows, and record
// the choice among the recent scopes. A pending portfolio drill-down is
// forgotten: the person has picked a scope of their own.
export function setWhere(where) {
  const { company, project, repository } = where;
  store.where = { company, project, repository };
  store.recent = pushRecent(store.recent, store.where);
  writeStored(storageKey("recent", store.payload.workspace_id), store.recent);
  store.beforeDrill = null;
  store.collapsed = new Set();
  requestRender();
}
