import { el } from "./el.js";
import { icon } from "./icon.js";
import { portfolioCells } from "./portfolio-cells.js";
import { roleBadges } from "./role-badges.js";

// A project or repository row; it opens All work, its blocked count the
// Blocked view, both filtered to it.
export function portfolioChildRow(child, onOpen) {
  const node = el("div", "prow prow-child");
  node.setAttribute("role", "row");
  const open = el("button", "prow-open");
  open.type = "button";
  open.append(
    icon(child.filter.project && !child.filter.repository ? "folder" : "repo"),
    el("span", "prow-name", child.label),
    ...roleBadges(child.roles),
  );
  open.addEventListener("click", () => onOpen("all"));
  const go = el("button", "icon-button small prow-end");
  go.type = "button";
  go.setAttribute("aria-label", `Open ${child.label}`);
  go.append(icon("chevronRight"));
  go.addEventListener("click", () => onOpen("all"));
  node.append(open, ...portfolioCells(child.buckets, () => onOpen("blocked")), go);
  return node;
}
