import { ruleValues } from "./rule-values.js";

// Whether a card passes one filter rule on `today`: "any" of the values,
// "not" any of them, or "empty" (no value). A "before:YYYY-MM-DD" due value
// holds for a due date before that day.
export function matchesRule(card, rule, today) {
  const values = ruleValues(card, rule.field, today);
  if (rule.op === "empty") {
    return rule.field === "due" ? card.due === null : values.length === 0;
  }
  const hit = rule.values.some((value) =>
    rule.field === "due" && value.startsWith("before:")
      ? card.due !== null && card.due < value.slice(7)
      : values.includes(value),
  );
  return rule.op === "not" ? !hit : hit;
}
