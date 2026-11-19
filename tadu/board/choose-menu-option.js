import { closeFilterMenu } from "./close-filter-menu.js";
import { menuRule } from "./menu-rule.js";
import { renderFilterMenu } from "./render-filter-menu.js";
import { setRule } from "./set-rule.js";

// Act on a Filter menu choice: a quick filter applies (or lifts) at once
// and closes the menu; a field opens its step; a value joins or leaves the
// field's rule, and the menu stays open for the next one.
export function chooseMenuOption(store, option) {
  const menu = store.menu;
  if (option.kind === "quick") {
    option.apply();
    closeFilterMenu(true);
    return;
  }
  const input = document.getElementById("filter-menu-input");
  if (option.kind === "field") {
    Object.assign(menu, { field: option.key, op: null, active: 0 });
    input.value = "";
  } else {
    const rule = menuRule(menu);
    const values = rule.op === "empty" ? [] : rule.values;
    const next = values.includes(option.key)
      ? values.filter((value) => value !== option.key)
      : [...values, option.key];
    const op = rule.op === "empty" ? "any" : rule.op;
    menu.op = op;
    menu.source.change(setRule(menu.source.rules(), { field: rule.field, op, values: next }));
  }
  renderFilterMenu(store);
}
