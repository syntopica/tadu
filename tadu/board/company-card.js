import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { icon } from "./icon.js";
import { relationBadge } from "./relation-badge.js";
import { rowMeta } from "./row-meta.js";

// The phone portfolio: one card per company (or relation) listing its
// projects with their relation badges, totals and per-state counts; the
// first three until "View all N projects" unfolds the rest. `drill(node)`
// gives a row's open action or null; `onMore` unfolds the card.
export function companyCard(group, unfolded, drill, onMore) {
  const card = el("section", "company-card");
  const head = el("header", "company-card-head");
  const open = drill(group);
  const name = el(open ? "button" : "span", "company-card-name");
  if (open) {
    name.type = "button";
    name.addEventListener("click", () => open(false));
  }
  const title = el("span", "company-card-title");
  title.append(el("strong", "", group.label), el("span", "muted", rowMeta(group)));
  name.append(icon(group.kind === "organization" ? "users" : "building", "icon group-icon"), title);
  head.append(name, el("span", "count", formatCount(group.buckets.total)));
  card.append(head);
  const list = el("div", "company-card-projects");
  const shown = unfolded ? group.children : group.children.slice(0, 3);
  for (const node of shown) {
    const action = drill(node);
    const line = el("button", "project-line");
    line.type = "button";
    line.disabled = action === null;
    line.addEventListener("click", () => action?.(false));
    const top = el("span", "project-line-top");
    top.append(
      icon(node.kind === "repository" ? "repo" : "folder"),
      el("span", "project-line-name", node.label),
      el("span", "count", formatCount(node.buckets.total)),
      icon("chevronRight", "icon row-chevron"),
    );
    const badges = el("span", "project-line-badges");
    badges.append(...node.relations.map(relationBadge));
    const counts = el("span", "project-line-counts");
    for (const [key, label] of [["backlog", "Backlog"], ["in_progress", "In progress"], ["blocked", "Blocked"]]) {
      const count = el("span", `state-count state-${key}`);
      count.append(el("span", "dot"), el("span", "", label), el("strong", "", formatCount(node.buckets[key])));
      counts.append(count);
    }
    line.append(top, ...(node.relations.length > 0 ? [badges] : []), counts);
    list.append(line);
  }
  card.append(list);
  if (group.children.length > 3) {
    const more = el("button", "column-more");
    more.type = "button";
    more.setAttribute("aria-expanded", String(unfolded));
    more.append(
      el("span", "", unfolded ? "Show fewer" : `View all ${formatCount(group.children.length)} projects`),
      icon(unfolded ? "chevronDown" : "arrowRight"),
    );
    more.addEventListener("click", onMore);
    card.append(more);
  }
  return card;
}
