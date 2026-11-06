import { FILTER_VALUES } from "./filter-values.js";

// The sorted distinct values cards offer to one filter.
export function distinctValues(cards, name) {
  return [...new Set(cards.flatMap(FILTER_VALUES[name]))].sort();
}
