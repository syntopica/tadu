import { OPEN_COLUMNS } from "./open-columns.js";
import { shiftDay } from "./shift-day.js";

// The Due date presets a card falls in on `today`: overdue (open and due
// before today), today, and the next 7 days (today included); none
// without a due date.
export function dueTags(card, today) {
  if (card.due === null) {
    return [];
  }
  const tags = [];
  if (OPEN_COLUMNS.includes(card.column) && card.due < today) {
    tags.push("overdue");
  }
  if (card.due === today) {
    tags.push("today");
  }
  if (card.due >= today && card.due <= shiftDay(today, 6)) {
    tags.push("week");
  }
  return tags;
}
