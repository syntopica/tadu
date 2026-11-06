import { cleanSavedView } from "./clean-saved-view.js";
import { savedViewsKey } from "./saved-views-key.js";

// One workspace's saved views from localStorage, each cleaned; an empty list
// when absent or unreadable.
export function loadSavedViews(workspaceId) {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(savedViewsKey(workspaceId)) ?? "[]");
    return Array.isArray(parsed) ? parsed.map(cleanSavedView).filter((view) => view !== null) : [];
  } catch {
    return [];
  }
}
