import { dueTags } from "./due-tags.js";
import { FILTER_VALUES } from "./filter-values.js";

// The values a card offers to one filter field on `today`: the Due date
// presets it falls in, or the field's own values.
export function ruleValues(card, field, today) {
  return field === "due" ? dueTags(card, today) : FILTER_VALUES[field](card);
}
