import { SAVED_VIEWS_KEY } from "./saved-views-key.js";

// Saved views from localStorage; an empty list when absent or unreadable.
export function loadSavedViews() {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(SAVED_VIEWS_KEY) ?? "[]");
    return Array.isArray(parsed) ? parsed.filter((v) => typeof v?.name === "string") : [];
  } catch {
    return [];
  }
}
