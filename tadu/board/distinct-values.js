import { FILTER_VALUES } from "./filter-values.js";

// The sorted distinct values cards offer to one filter field (not the due
// date, whose values are presets).
export function distinctValues(cards, name) {
  return [...new Set(cards.flatMap(FILTER_VALUES[name]))].sort();
}
