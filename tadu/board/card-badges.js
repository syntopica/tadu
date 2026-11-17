import { avatar } from "./avatar.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { kindBadge } from "./kind-badge.js";
import { priorityBadge } from "./priority-badge.js";

// The optional facts of a card, only those it has: priority, a kind other
// than task, due date, check date, labels and assignees; priority and kind only when
// `shown` allows them.
export function cardBadges(card, shown) {
  const row = el("span", "badges");
  const priority = shown.priority ? priorityBadge(card.priority) : null;
  if (priority) {
    row.append(priority);
  }
  const kind = shown.kind ? kindBadge(card.kind) : null;
  if (kind) {
    row.append(kind);
  }
  if (card.due !== null) {
    const due = el("span", "due");
    due.append(icon("calendar"), el("span", "", card.due));
    row.append(due);
  }
  if (card.check_on !== null) {
    const check = el("span", "due check-on");
    check.title = "Check on";
    check.append(icon("clock"), el("span", "", card.check_on));
    row.append(check);
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
