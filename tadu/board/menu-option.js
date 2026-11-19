import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { icon } from "./icon.js";

// One choice of the Filter menu as a listbox option: a check for what is
// on (a dot for a field that has a rule), the field's or quick filter's
// icon, the label and its count. `at` is
// its place in the list, which clicks and the arrow keys use.
export function menuOption(option, at, active) {
  const item = el("li", `menu-option ${option.kind}`);
  item.id = `filter-menu-option-${at}`;
  item.dataset.at = String(at);
  item.setAttribute("role", "option");
  item.setAttribute("aria-selected", String(option.checked));
  item.classList.toggle("active", active);
  // A field is a step, not a choice: it shows a dot while it has a rule instead of a check.
  const check = el("span", "menu-check");
  if (option.checked && option.kind !== "field") {
    check.append(icon("check"));
  }
  item.append(check);
  if (option.icon) {
    item.append(icon(option.icon, "icon menu-icon"));
  }
  item.append(el("span", "menu-label", option.label));
  if (option.count !== null) {
    item.append(el("span", "menu-count", formatCount(option.count)));
  } else if (option.kind === "field") {
    item.append(icon("chevronRight", "icon menu-count"));
  }
  return item;
}
