import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { icon } from "./icon.js";

// The number cells of one portfolio row; a blocked count above zero opens
// the Blocked view for that row when `onBlocked` is given.
export function portfolioCells(buckets, onBlocked) {
  const cell = (value, className = "") => el("span", `num ${className}`.trim(), formatCount(value));
  const blocked = el("span", "num blocked-cell");
  if (buckets.blocked > 0 && onBlocked) {
    const link = el("button", "blocked-link");
    link.type = "button";
    link.setAttribute("aria-label", `Open ${buckets.blocked} blocked items`);
    link.append(el("span", "", formatCount(buckets.blocked)), icon("arrowRight"));
    link.addEventListener("click", (event) => {
      event.stopPropagation();
      onBlocked();
    });
    blocked.append(link);
  } else {
    blocked.textContent = formatCount(buckets.blocked);
    blocked.classList.toggle("has-blocked", buckets.blocked > 0);
  }
  return [
    cell(buckets.total, "total"),
    cell(buckets.backlog),
    cell(buckets.in_progress),
    blocked,
    cell(buckets.done),
  ];
}
