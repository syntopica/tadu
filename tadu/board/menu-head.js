import { el } from "./el.js";
import { icon } from "./icon.js";
import { OP_TITLES } from "./op-titles.js";

// The head of the Filter menu: "Filter by" on its first step; on a field's
// step, Back (unless the menu opened on that field), the field's title and
// a choice of how its rule matches (`rule.op`), which `onOp` hears.
export function menuHead(menu, field, rule, handlers) {
  const title = el("h2", "menu-title", field ? field.title : "Filter by");
  title.id = "filter-menu-title";
  if (field === null) {
    return [title];
  }
  const parts = [];
  if (!menu.direct) {
    const back = el("button", "icon-button small menu-back");
    back.type = "button";
    back.setAttribute("aria-label", "Back to the fields");
    back.append(icon("chevronLeft"));
    back.addEventListener("click", handlers.onBack);
    parts.push(back);
  }
  parts.push(title);
  if (field.ops.length > 1) {
    const ops = el("div", "menu-ops");
    ops.setAttribute("role", "radiogroup");
    ops.setAttribute("aria-label", `How ${field.title} matches`);
    for (const op of field.ops) {
      const button = el("button", "menu-op", OP_TITLES[op]);
      button.type = "button";
      button.setAttribute("role", "radio");
      button.setAttribute("aria-checked", String(op === rule.op));
      button.addEventListener("click", () => handlers.onOp(op));
      ops.append(button);
    }
    parts.push(ops);
  }
  return parts;
}
