import { el } from "./el.js";
import { icon } from "./icon.js";
import { portfolioCells } from "./portfolio-cells.js";
import { roleBadges } from "./role-badges.js";

// A project or repository row; it opens the list of the cards it counts,
// its blocked count the Blocked view of those cards. `onOpen(blocked)`.
export function portfolioChildRow(child, onOpen) {
  const node = el("div", "prow prow-child");
  node.setAttribute("role", "row");
  const open = el("button", "prow-open");
  open.type = "button";
  open.append(
    icon(child.filter.repository ? "repo" : "folder"),
    el("span", "prow-name", child.label),
    ...roleBadges(child.roles),
  );
  open.setAttribute("aria-label", `Open the items of ${child.label}`);
  open.addEventListener("click", () => onOpen(false));
  const go = el("button", "icon-button small prow-end");
  go.type = "button";
  go.setAttribute("aria-label", `Open the items of ${child.label}`);
  go.append(icon("chevronRight"));
  go.addEventListener("click", () => onOpen(false));
  node.append(open, ...portfolioCells(child.buckets, child.label, () => onOpen(true)), go);
  return node;
}
