import { el } from "./el.js";
import { setRule } from "./set-rule.js";

// The foot of a field's step in the Filter menu: for the due date, a day
// to add as "before" it; and Remove while the field has a rule. Each
// change goes through the menu's source, then `redraw` draws the menu.
export function menuFoot(menu, field, rule, redraw) {
  if (field === null) {
    return [];
  }
  const source = menu.source;
  const parts = [];
  if (field.key === "due") {
    const label = el("label", "menu-day", "Before");
    const day = el("input");
    day.type = "date";
    day.addEventListener("change", () => {
      if (day.value !== "") {
        const values = rule.op === "empty" ? [] : rule.values;
        const op = rule.op === "empty" ? "any" : rule.op;
        source.change(setRule(source.rules(), { field: "due", op, values: [...new Set([...values, `before:${day.value}`])] }));
        redraw();
      }
    });
    label.append(day);
    parts.push(label);
  }
  if (source.rules().some((entry) => entry.field === field.key)) {
    const remove = el("button", "link-button menu-remove", "Remove filter");
    remove.type = "button";
    remove.addEventListener("click", () => {
      source.change(source.rules().filter((entry) => entry.field !== field.key));
      redraw();
    });
    parts.push(remove);
  }
  return parts;
}
