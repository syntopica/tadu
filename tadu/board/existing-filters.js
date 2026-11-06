import { distinctValues } from "./distinct-values.js";
import { PRIORITY_TITLES } from "./priority-titles.js";

// Filters with every value the current data no longer offers reset to ""
// (any), so a restored filter never hides behind a select showing "Any".
export function existingFilters(filters, cards, columns) {
  const result = { ...filters };
  for (const name of ["repository", "project", "organization", "role", "assignee", "label"]) {
    if (result[name] !== "" && !distinctValues(cards, name).includes(result[name])) {
      result[name] = "";
    }
  }
  if (!(result.priority in PRIORITY_TITLES)) {
    result.priority = "";
  }
  if (!columns.includes(result.column)) {
    result.column = "";
  }
  return result;
}
