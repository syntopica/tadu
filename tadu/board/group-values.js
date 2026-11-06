import { COLUMN_TITLES } from "./column-titles.js";
import { LAST_ORDER } from "./last-order.js";
import { newestFirst } from "./newest-first.js";
import { PRIORITY_TITLES } from "./priority-titles.js";
import { priorityRank } from "./priority-rank.js";
import { STATE_ORDER } from "./state-order.js";

// The groups a card falls in, each {key, label, order}: one group, except
// that a card with several assignees is in each assignee's group.
export function groupValues(card, group) {
  switch (group) {
    case "company":
      return card.place.company === ""
        ? [{ key: "", label: "No company", order: LAST_ORDER }]
        : [{ key: card.place.company, label: card.place.company, order: card.place.company }];
    case "project":
      return card.project === null
        ? [{ key: "", label: "No project", order: LAST_ORDER }]
        : [{ key: card.project, label: card.place.project, order: card.place.project }];
    case "repository":
      return [{ key: card.repository, label: card.repository, order: card.repository }];
    case "priority":
      return [
        {
          key: card.priority ?? "",
          label: PRIORITY_TITLES[card.priority] ?? "No priority",
          order: String(priorityRank(card.priority)),
        },
      ];
    case "assignee":
      return card.assignees.length === 0
        ? [{ key: "", label: "Unassigned", order: LAST_ORDER }]
        : card.assignees.map((person) => ({ key: person, label: person, order: person }));
    case "day":
      return card.day === null
        ? [{ key: "", label: "No closing day", order: LAST_ORDER }]
        : [{ key: card.day, label: card.day, order: newestFirst(card.day) }];
    default:
      return [
        {
          key: card.column,
          label: COLUMN_TITLES[card.column] ?? card.column,
          order: String(STATE_ORDER.indexOf(card.column)),
        },
      ];
  }
}
