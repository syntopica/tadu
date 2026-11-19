import { COLUMN_TITLES } from "./column-titles.js";
import { distinctValues } from "./distinct-values.js";
import { DUE_PRESETS } from "./due-presets.js";
import { KIND_FILTER_TITLES } from "./kind-filter-titles.js";
import { matchesRule } from "./matches-rule.js";
import { PRIORITY_TITLES } from "./priority-titles.js";
import { valueLabel } from "./value-label.js";

// The values the Filter menu offers for one field, each {value, label,
// count} with how many of `cards` hold it: states in board order,
// priorities and kinds in theirs, the due presets, else the values the
// cards hold (me first among assignees). A value already `chosen` that no
// card holds stays, so it can be turned off. `context` holds today,
// columns, names (organization display names) and me.
export function fieldValues(field, cards, context, chosen) {
  const fixed = {
    state: context.columns.filter((column) => column in COLUMN_TITLES),
    priority: Object.keys(PRIORITY_TITLES),
    kind: Object.keys(KIND_FILTER_TITLES),
    due: DUE_PRESETS.map(([key]) => key),
  };
  let values = fixed[field] ?? distinctValues(cards, field);
  if (field === "assignee" && values.includes(context.me)) {
    values = [context.me, ...values.filter((value) => value !== context.me)];
  }
  values = [...values, ...chosen.filter((value) => !values.includes(value))];
  return values.map((value) => ({
    value,
    label: valueLabel(field, value, context.names, context.me),
    count: cards.filter((card) => matchesRule(card, { field, op: "any", values: [value] }, context.today))
      .length,
  }));
}
