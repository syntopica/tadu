import { COLUMN_TITLES } from "./column-titles.js";
import { distinctValues } from "./distinct-values.js";
import { DUE_PRESETS } from "./due-presets.js";
import { KIND_FILTER_TITLES } from "./kind-filter-titles.js";
import { PRIORITY_TITLES } from "./priority-titles.js";
import { setRule } from "./set-rule.js";

// Filters with every value the current data no longer offers taken out,
// and a rule left with none dropped, so a restored filter never hides
// what it keeps behind a value that cannot be seen or turned off.
export function existingFilters(filters, cards, columns) {
  const offered = (field, value) => {
    if (field === "state") {
      return columns.includes(value) && Object.hasOwn(COLUMN_TITLES, value);
    }
    if (field === "due") {
      return DUE_PRESETS.some(([key]) => key === value) || /^before:\d{4}-\d{2}-\d{2}$/.test(value);
    }
    const fixed = { priority: PRIORITY_TITLES, kind: KIND_FILTER_TITLES }[field];
    return fixed ? Object.hasOwn(fixed, value) : distinctValues(cards, field).includes(value);
  };
  let rules = [];
  for (const rule of filters.rules) {
    rules = setRule(rules, { ...rule, values: rule.values.filter((value) => offered(rule.field, value)) });
  }
  return { ...filters, rules };
}
