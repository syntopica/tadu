import { ITEM_FIELDS } from "./item-fields.js";
import { legacyRules } from "./legacy-rules.js";

// A filter choice as stored (a saved view's) made well formed: rules of
// known fields with a way of matching the field allows and text values,
// one rule per field, and the two toggles. A choice saved before rules
// existed is read by legacyRules.
export function cleanFilters(raw) {
  const source = raw !== null && typeof raw === "object" ? raw : {};
  const given = Array.isArray(source.rules) ? source.rules : legacyRules(source);
  const rules = [];
  for (const rule of given) {
    const field = ITEM_FIELDS.find((entry) => entry.key === rule?.field);
    if (!field || !field.ops.includes(rule.op) || rules.some((old) => old.field === field.key)) {
      continue;
    }
    const values = Array.isArray(rule.values) ? rule.values.filter((value) => typeof value === "string") : [];
    if (rule.op === "empty" || values.length > 0) {
      rules.push({ field: field.key, op: rule.op, values: rule.op === "empty" ? [] : [...new Set(values)] });
    }
  }
  return { rules, waitingOnMe: source.waitingOnMe === true, showCancelled: source.showCancelled === true };
}
