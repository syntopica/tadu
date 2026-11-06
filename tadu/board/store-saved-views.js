import { SAVED_VIEWS_KEY } from "./saved-views-key.js";

// Keep the saved views in this browser's localStorage; the page writes no file.
export function storeSavedViews(views) {
  try {
    window.localStorage.setItem(SAVED_VIEWS_KEY, JSON.stringify(views));
  } catch {
    // Storage full or disabled: the views last until the tab closes.
  }
}
