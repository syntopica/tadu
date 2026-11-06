import { savedViewsKey } from "./saved-views-key.js";

// Keep one workspace's saved views in this browser's localStorage; the page
// writes no file.
export function storeSavedViews(views, workspaceId) {
  try {
    window.localStorage.setItem(savedViewsKey(workspaceId), JSON.stringify(views));
  } catch {
    // Storage full or disabled: the views last until the tab closes.
  }
}
