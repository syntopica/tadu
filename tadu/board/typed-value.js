import { COLUMN_TITLES } from "./column-titles.js";
import { distinctValues } from "./distinct-values.js";
import { DUE_PRESETS } from "./due-presets.js";
import { KIND_FILTER_TITLES } from "./kind-filter-titles.js";
import { PRIORITY_TITLES } from "./priority-titles.js";
import { resolveChoice } from "./resolve-choice.js";

// The filter value a typed one names for `field`, or null: a state,
// priority, kind or due preset by its key or title in any case, spaces,
// hyphens and underscores aside ("in-progress"); a due day as "before" it;
// "me" as the board's person; else the one value of the cards that it
// names as resolveChoice reads it ("Organization" values are "role:org").
export function typedValue(field, typed, cards, me) {
  const plain = (text) => text.toLowerCase().replace(/[\s_-]/g, "");
  const fixed = {
    state: COLUMN_TITLES,
    priority: PRIORITY_TITLES,
    kind: KIND_FILTER_TITLES,
    due: Object.fromEntries(DUE_PRESETS),
  }[field];
  if (fixed) {
    const found = Object.entries(fixed).find(([key, title]) => plain(key) === plain(typed) || plain(title) === plain(typed));
    if (found) {
      return found[0];
    }
    return field === "due" && /^\d{4}-\d{2}-\d{2}$/.test(typed) ? `before:${typed}` : null;
  }
  if (field === "assignee" && typed.toLowerCase() === "me") {
    return me;
  }
  const value = resolveChoice(typed, distinctValues(cards, field));
  return value === "" ? null : value;
}
