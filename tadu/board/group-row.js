import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { icon } from "./icon.js";

// A list group header that collapses or expands its group.
export function groupRow(row, onToggle) {
  const button = el("button", "group-row");
  button.type = "button";
  button.setAttribute("aria-expanded", String(!row.closed));
  button.append(
    icon(row.closed ? "chevronRight" : "chevronDown"),
    el("span", "group-label", row.label),
    el("span", "count", formatCount(row.count)),
  );
  button.addEventListener("click", () => onToggle(row.key));
  return button;
}
