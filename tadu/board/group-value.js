import { COLUMN_TITLES } from "./column-titles.js";
import { newestFirst } from "./newest-first.js";
import { PRIORITY_TITLES } from "./priority-titles.js";
import { priorityRank } from "./priority-rank.js";

const STATE_ORDER = ["blocked", "in_progress", "ready", "backlog", "done", "cancelled"];
const LAST = "￿";

// The group a card falls in: key, label and a sortable order.
export function groupValue(card, group) {
  switch (group) {
    case "project":
      return card.project === null
        ? { key: "", label: "No project", order: LAST }
        : { key: card.project, label: card.project, order: card.project };
    case "repository":
      return { key: card.repository, label: card.repository, order: card.repository };
    case "priority":
      return {
        key: card.priority ?? "",
        label: PRIORITY_TITLES[card.priority] ?? "No priority",
        order: String(priorityRank(card.priority)),
      };
    case "assignee":
      return card.assignees.length === 0
        ? { key: "", label: "Unassigned", order: LAST }
        : { key: card.assignees[0], label: card.assignees[0], order: card.assignees[0] };
    case "day":
      return card.day === null
        ? { key: "", label: "No closing day", order: LAST }
        : { key: card.day, label: card.day, order: newestFirst(card.day) };
    default:
      return {
        key: card.column,
        label: COLUMN_TITLES[card.column] ?? card.column,
        order: String(STATE_ORDER.indexOf(card.column)),
      };
  }
}
