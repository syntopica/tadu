import { el } from "./el.js";
import { icon } from "./icon.js";
import { portfolioCells } from "./portfolio-cells.js";
import { relationBadge } from "./relation-badge.js";
import { rowMeta } from "./row-meta.js";

// One row of the portfolio tree at `depth` (0 company or relation, 1
// project, 2 repository): a chevron that folds its children, its name and
// the chevron at the end open its items in that scope, and its blocked
// count opens the Blocked view of them. `actions` holds {open, onToggle,
// onOpen(blocked)}; onOpen is null for a row that opens nothing.
export function portfolioRow(node, depth, actions) {
  const row = el("div", `prow prow-depth-${depth} prow-${node.kind}`);
  row.setAttribute("role", "row");
  const name = el("div", "prow-name-cell");
  if (node.children.length > 0) {
    const toggle = el("button", "prow-toggle");
    toggle.type = "button";
    toggle.setAttribute("aria-expanded", String(actions.open));
    toggle.setAttribute("aria-label", `${actions.open ? "Hide" : "Show"} what ${node.label} holds`);
    toggle.append(icon(actions.open ? "chevronDown" : "chevronRight"));
    toggle.addEventListener("click", actions.onToggle);
    name.append(toggle);
  } else {
    name.append(el("span", "prow-spacer"));
  }
  const kinds = { company: "building", organization: "users", project: "folder", repository: "repo" };
  const iconName = node.last ? "folder" : kinds[node.kind];
  const label = el(actions.onOpen ? "button" : "span", "prow-open");
  if (actions.onOpen) {
    label.type = "button";
    label.setAttribute("aria-label", `Open the items of ${node.label}`);
    label.addEventListener("click", () => actions.onOpen(false));
  }
  label.append(
    icon(iconName, depth === 0 ? "icon group-icon" : "icon"),
    el("span", "prow-name", node.label),
  );
  name.append(label);
  const meta = rowMeta(node);
  if (meta !== "") {
    name.append(el("span", "prow-meta muted", meta));
  }
  name.append(...node.relations.map(relationBadge));
  const blocked = actions.onOpen ? () => actions.onOpen(true) : null;
  row.append(name, ...portfolioCells(node.buckets, node.label, blocked));
  if (actions.onOpen) {
    const go = el("button", "icon-button small prow-end");
    go.type = "button";
    go.setAttribute("aria-label", `Open the items of ${node.label}`);
    go.append(icon("chevronRight"));
    go.addEventListener("click", () => actions.onOpen(false));
    row.append(go);
  } else {
    row.append(el("span", "prow-end"));
  }
  return row;
}
