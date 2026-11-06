import { hashText } from "./hash-text.js";
import { storageKey } from "./storage-key.js";
import { writeStored } from "./write-stored.js";

// Keep the URL hash on the current scope and view, so the address reopens
// them, and remember the scope for the next visit to this workspace.
export function syncLocation(store) {
  if (!store.payload) {
    return;
  }
  const hash = hashText(store.where, store.view);
  if (hash !== window.location.hash) {
    window.history.replaceState(null, "", hash);
  }
  const stored = JSON.stringify(store.where);
  if (stored !== store.storedWhere) {
    store.storedWhere = stored;
    writeStored(storageKey("scope", store.payload.workspace_id), store.where);
  }
}
