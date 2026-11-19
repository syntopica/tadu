import { el } from "./el.js";
import { icon } from "./icon.js";

// One active filter as a chip: a button reading "Assignee · is any of ·
// Ana, Bo" that opens its editor (`onOpen` gets the button), and a remove
// button. `parts` is what ruleParts gives; a quick toggle has only a title.
export function filterChip(parts, onOpen, onRemove) {
  const chip = el("span", "filter-chip");
  const main = el("button", "filter-chip-main");
  main.type = "button";
  main.dataset.filterAnchor = "";
  main.setAttribute("aria-haspopup", "dialog");
  main.setAttribute("aria-expanded", "false");
  main.append(el("span", "chip-field", parts.title));
  if (parts.op) {
    main.append(el("span", "chip-op", parts.op));
  }
  if (parts.values) {
    main.append(el("span", "chip-values", parts.values));
  }
  main.addEventListener("click", () => onOpen(main));
  const remove = el("button", "chip-remove");
  remove.type = "button";
  remove.setAttribute("aria-label", `Remove the ${parts.title} filter`);
  remove.append(icon("close"));
  remove.addEventListener("click", onRemove);
  chip.append(main, remove);
  return chip;
}
