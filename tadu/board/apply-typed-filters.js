import { parseQuery } from "./parse-query.js";
import { setRule } from "./set-rule.js";
import { typedValue } from "./typed-value.js";

// Turn the typed filters of the search box into rules and chips, and leave
// the rest of its text as the search: a value joins the field's rule when
// that matches the same way, else the rule is replaced. `final` is true on
// Enter, when the last word counts too. Returns whether anything changed.
export function applyTypedFilters(store, input, final) {
  const me = store.payload?.me ?? null;
  const parsed = parseQuery(input.value, final, (field, typed) => typedValue(field, typed, store.cards, me));
  if (parsed.filters.length === 0) {
    return false;
  }
  let { rules, waitingOnMe } = store.filters;
  for (const filter of parsed.filters) {
    if (filter.toggle) {
      waitingOnMe = true;
      continue;
    }
    const values = filter.values.map((value) => (value === "@me" ? me : value)).filter((value) => value !== null);
    const old = rules.find((rule) => rule.field === filter.field);
    const joined = old && old.op === filter.op && filter.op !== "empty" ? [...old.values, ...values] : values;
    if (filter.op === "empty" || joined.length > 0) {
      rules = setRule(rules, { field: filter.field, op: filter.op, values: [...new Set(joined)] });
    }
  }
  store.filters = { ...store.filters, rules, waitingOnMe };
  input.value = parsed.text;
  store.text = parsed.text.trim();
  return true;
}
