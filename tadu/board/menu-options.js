import { matchesQuery } from "./matches-query.js";

// The choices of the open Filter menu that match what is typed, each
// {kind, key, label, icon, count, checked}. On its first step: the quick
// filters ("quick") then the fields ("field"), or with text typed those
// whose name starts with it first; on a field's step, that field's values
// ("value"), checked when its rule holds them.
export function menuOptions(menu, text) {
  const keep = (option) => matchesQuery(option.label.toLowerCase(), text.trim());
  const source = menu.source;
  if (menu.field === null) {
    const quick = source.quick().map((entry) => ({
      kind: "quick",
      key: entry.key,
      label: entry.title,
      icon: entry.icon,
      count: entry.count,
      checked: entry.active,
      apply: entry.apply,
    }));
    const fields = source.fields().map((field) => ({
      kind: "field",
      key: field.key,
      label: field.title,
      icon: field.icon,
      count: null,
      checked: source.rules().some((rule) => rule.field === field.key),
    }));
    // Typing a field's name most likely asks for the field: names that start with the text
    // come first, fields before quick filters.
    const typed = text.trim().toLowerCase();
    const rank = (option) => (option.label.toLowerCase().startsWith(typed) ? 0 : 2) + (option.kind === "quick" ? 1 : 0);
    const found = [...quick, ...fields].filter(keep);
    return typed === "" ? found : found.sort((a, b) => rank(a) - rank(b));
  }
  const rule = source.rules().find((entry) => entry.field === menu.field);
  const chosen = rule?.op === "empty" ? [] : (rule?.values ?? []);
  return source
    .values(menu.field, chosen)
    .map((entry) => ({
      kind: "value",
      key: entry.value,
      label: entry.label,
      icon: null,
      count: entry.count,
      checked: chosen.includes(entry.value),
    }))
    .filter(keep);
}
