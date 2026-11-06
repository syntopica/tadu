import { el } from "./el.js";
import { icon } from "./icon.js";
import { portfolioCells } from "./portfolio-cells.js";
import { roleBadges } from "./role-badges.js";

// An organization or project row that folds its children.
export function portfolioGroupRow(row, closed, groupBy, onToggle) {
  const node = el("div", "prow prow-group");
  node.setAttribute("role", "row");
  const toggle = el("button", "prow-toggle");
  toggle.type = "button";
  toggle.setAttribute("aria-expanded", String(!closed));
  const kind = row.last ? "folder" : groupBy === "organization" ? "building" : "branch";
  toggle.append(
    icon(closed ? "chevronRight" : "chevronDown"),
    icon(kind, "icon group-icon"),
    el("span", "prow-name", row.label),
    ...roleBadges(row.roles),
  );
  toggle.addEventListener("click", onToggle);
  node.append(toggle, ...portfolioCells(row.buckets, row.label, null), el("span", "prow-end"));
  return node;
}
