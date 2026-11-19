import { el } from "./el.js";
import { menuFoot } from "./menu-foot.js";
import { menuHead } from "./menu-head.js";
import { menuOption } from "./menu-option.js";
import { menuOptions } from "./menu-options.js";
import { menuRule } from "./menu-rule.js";
import { setRule } from "./set-rule.js";

// Draw the open Filter menu from store.menu: its head, the choices that
// match what is typed (grouped on the first step), the active one marked
// for the arrow keys, and the foot of a field's step.
export function renderFilterMenu(store) {
  const menu = store.menu;
  const input = document.getElementById("filter-menu-input");
  const options = menuOptions(menu, input.value);
  menu.options = options;
  menu.active = Math.min(Math.max(menu.active, 0), Math.max(options.length - 1, 0));
  const field = menu.field === null ? null : menu.source.fields().find((entry) => entry.key === menu.field);
  const rule = field ? menuRule(menu) : null;
  const redraw = () => renderFilterMenu(store);
  const handlers = {
    onBack: () => {
      Object.assign(menu, { field: null, op: null, active: 0 });
      input.value = "";
      redraw();
      input.focus();
    },
    onOp: (op) => {
      menu.op = op;
      const values = op === "empty" ? [] : rule.values;
      if (op === "empty" || values.length > 0) {
        menu.source.change(setRule(menu.source.rules(), { field: rule.field, op, values }));
      }
      redraw();
    },
  };
  document.getElementById("filter-menu-head").replaceChildren(...menuHead(menu, field, rule, handlers));
  input.placeholder = field ? `Search ${field.title.toLowerCase()}…` : "Search…";
  const list = document.getElementById("filter-menu-list");
  list.setAttribute("aria-multiselectable", String(field !== null));
  const nodes = [];
  let group = "";
  options.forEach((option, at) => {
    const heading = { quick: "Quick", field: "Properties" }[option.kind];
    if (heading && heading !== group) {
      const head = el("li", "picker-group", heading);
      head.setAttribute("role", "presentation");
      nodes.push(head);
      group = heading;
    }
    nodes.push(menuOption(option, at, at === menu.active));
  });
  const empty = rule?.op === "empty" ? `Keeps items with no ${field.title.toLowerCase()}.` : "Nothing matches.";
  list.replaceChildren(...(nodes.length > 0 && rule?.op !== "empty" ? nodes : [el("li", "picker-empty", empty)]));
  document.getElementById("filter-menu-foot").replaceChildren(...menuFoot(menu, field, rule, redraw));
  // A control redrawn under the focus (after a click on it) hands the focus back to the search.
  if (!document.getElementById("filter-menu").contains(document.activeElement)) {
    input.focus();
  }
  if (options.length > 0 && rule?.op !== "empty") {
    input.setAttribute("aria-activedescendant", `filter-menu-option-${menu.active}`);
    document.getElementById(`filter-menu-option-${menu.active}`).scrollIntoView({ block: "nearest" });
  } else {
    input.removeAttribute("aria-activedescendant");
  }
}
