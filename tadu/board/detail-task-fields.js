import { detailField } from "./detail-field.js";
import { el } from "./el.js";

// The task fields of a format 2 card (category, type, milestone, the day it
// may start and the day it started), only those it has; null for a card
// with none, such as a TODO.md item.
export function detailTaskFields(card) {
  const fields = [
    ["Category", "folder", card.category],
    ["Type", "tag", card.type],
    ["Milestone", "bookmark", card.milestone],
    ["Defer until", "calendar", card.defer_until],
    ["Started", "clock", card.started],
  ].filter(([, , value]) => value !== null && value !== undefined);
  if (fields.length === 0) {
    return null;
  }
  const list = el("dl", "fields task-fields");
  for (const [label, iconName, value] of fields) {
    list.append(...detailField(label, iconName, value));
  }
  return list;
}
