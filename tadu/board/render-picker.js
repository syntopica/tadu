import { el } from "./el.js";
import { pickerOptions } from "./picker-options.js";
import { sameWhere } from "./same-where.js";

// Fill the open scope picker with the choices matching what is typed,
// grouped by kind, the active one marked for the arrow keys.
export function renderPicker(store) {
  const state = store.picker;
  const input = document.getElementById("picker-input");
  const options = pickerOptions(state.kind, store.index, store.where, input.value, store);
  state.options = options;
  state.active = Math.min(Math.max(state.active, 0), Math.max(options.length - 1, 0));
  const nodes = [];
  let group = "";
  options.forEach((option, at) => {
    if (option.group !== "" && option.group !== group) {
      const head = el("li", "picker-group", option.group);
      head.setAttribute("role", "presentation");
      nodes.push(head);
    }
    group = option.group;
    const item = el("li", "picker-option");
    item.id = `picker-option-${at}`;
    item.dataset.at = String(at);
    item.setAttribute("role", "option");
    item.setAttribute("aria-selected", String(at === state.active));
    item.classList.toggle("current", sameWhere(option.target, store.where));
    item.append(el("span", "picker-label", option.label));
    if (option.detail !== "") {
      item.append(el("span", "picker-detail", option.detail));
    }
    nodes.push(item);
  });
  if (options.length === 0) {
    nodes.push(el("li", "picker-empty", "Nothing matches."));
  }
  document.getElementById("picker-list").replaceChildren(...nodes);
  if (options.length > 0) {
    input.setAttribute("aria-activedescendant", `picker-option-${state.active}`);
    document.getElementById(`picker-option-${state.active}`).scrollIntoView({ block: "nearest" });
  } else {
    input.removeAttribute("aria-activedescendant");
  }
}
