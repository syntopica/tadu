// The rules with `rule` in place of the one of its field (or added last),
// or without that field when the rule keeps nothing apart: no values and
// not "empty".
export function setRule(rules, rule) {
  const drop = rule.op !== "empty" && rule.values.length === 0;
  const kept = { field: rule.field, op: rule.op, values: rule.op === "empty" ? [] : [...rule.values] };
  const at = rules.findIndex((old) => old.field === rule.field);
  if (at === -1) {
    return drop ? [...rules] : [...rules, kept];
  }
  return drop ? rules.filter((_, other) => other !== at) : rules.map((old, other) => (other === at ? kept : old));
}
