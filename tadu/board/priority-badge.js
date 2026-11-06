import { el } from "./el.js";
import { PRIORITY_TITLES } from "./priority-titles.js";

// "Urgent", "High", "Normal" or "Low"; null for a card without a priority.
export function priorityBadge(priority) {
  if (priority === null || !(priority in PRIORITY_TITLES)) {
    return null;
  }
  return el("span", `badge priority-${priority}`, PRIORITY_TITLES[priority]);
}
