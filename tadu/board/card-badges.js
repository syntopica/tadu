import { avatar } from "./avatar.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { priorityBadge } from "./priority-badge.js";

// The optional facts of a card, only those it has: priority, due date,
// labels and assignees.
export function cardBadges(card) {
  const row = el("span", "badges");
  const priority = priorityBadge(card.priority);
  if (priority) {
    row.append(priority);
  }
  if (card.due !== null) {
    const due = el("span", "due");
    due.append(icon("calendar"), el("span", "", card.due));
    row.append(due);
  }
  for (const label of card.labels.slice(0, 2)) {
    row.append(el("span", "label", label));
  }
  if (card.assignees.length > 0) {
    const people = el("span", "people");
    people.append(...card.assignees.slice(0, 3).map(avatar));
    row.append(people);
  }
  return row;
}
