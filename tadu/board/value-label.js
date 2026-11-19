import { capitalize } from "./capitalize.js";
import { COLUMN_TITLES } from "./column-titles.js";
import { DUE_PRESETS } from "./due-presets.js";
import { KIND_FILTER_TITLES } from "./kind-filter-titles.js";
import { PRIORITY_TITLES } from "./priority-titles.js";

// How a filter value reads on a chip and in the Filter menu: a state,
// priority or kind by its title, a due preset or "Before 2026-12-01", a
// relation as "Client: Automate Texas" (display names from `names`), and
// me as "ana (me)".
export function valueLabel(field, value, names, me) {
  const titles = { state: COLUMN_TITLES, priority: PRIORITY_TITLES, kind: KIND_FILTER_TITLES };
  if (Object.hasOwn(titles, field)) {
    return Object.hasOwn(titles[field], value) ? titles[field][value] : value;
  }
  if (field === "due") {
    const preset = DUE_PRESETS.find(([key]) => key === value);
    return preset ? preset[1] : `Before ${value.replace(/^before:/, "")}`;
  }
  if (field === "organization") {
    const [role, ...org] = value.split(":");
    const id = org.join(":");
    return `${capitalize(role)}: ${names.get(id) ?? id}`;
  }
  return field === "assignee" && value === me ? `${value} (me)` : value;
}
