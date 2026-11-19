import { OP_TITLES } from "./op-titles.js";

// How a filter chip reads a rule: the field's title, how it matches ("is"
// for one value, "is any of" for several, "is not", "is empty") and its
// values by `label`, at most two named and the rest counted ("+2").
export function ruleParts(rule, title, label) {
  const op = rule.op === "any" && rule.values.length === 1 ? "is" : OP_TITLES[rule.op];
  const named = rule.values.slice(0, 2).map(label).join(", ");
  const more = rule.values.length > 2 ? ` +${rule.values.length - 2}` : "";
  return { title, op, values: rule.op === "empty" ? "" : `${named}${more}` };
}
