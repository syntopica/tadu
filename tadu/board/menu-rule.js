// The rule the Filter menu edits on a field's step: the field's own, else
// a new one that matches the way chosen on that step (menu.op) or the
// field's first.
export function menuRule(menu) {
  const found = menu.source.rules().find((rule) => rule.field === menu.field);
  if (found) {
    return found;
  }
  const field = menu.source.fields().find((entry) => entry.key === menu.field);
  return { field: menu.field, op: menu.op ?? field.ops[0], values: [] };
}
