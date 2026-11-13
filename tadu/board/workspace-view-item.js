import { navItem } from "./nav-item.js";

// A read-only sidebar row for a view the workspace file defines; its criteria
// show as the tooltip.
export function workspaceViewItem(view) {
  const item = navItem(view.name, "bookmark", false, () => {});
  item.title = view.criteria === "" ? "No criteria" : view.criteria;
  item.disabled = true;
  return item;
}
