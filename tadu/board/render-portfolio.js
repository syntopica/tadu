import { applyFilter } from "./apply-filter.js";
import { el } from "./el.js";
import { filterTree } from "./filter-tree.js";
import { formatCount } from "./format-count.js";
import { portfolioChildRow } from "./portfolio-child-row.js";
import { portfolioGroupRow } from "./portfolio-group-row.js";
import { portfolioCards } from "./portfolio-cards.js";
import { portfolioTarget } from "./portfolio-target.js";
import { portfolioTree } from "./portfolio-tree.js";
import { requestRender } from "./request-render.js";
import { statCard } from "./stat-card.js";
import { treeTotals } from "./tree-totals.js";

// Stat cards and the table of organizations (or projects) with their counts.
export function renderPortfolio(store, content) {
  const { groupBy, role, state, text, collapsed } = store.portfolio;
  const cards = portfolioCards(store.cards, store.portfolio, store.filters.project);
  const totals = treeTotals(cards);
  const days = store.payload.done_days;
  const stats = el("div", "stats");
  stats.append(
    statCard(totals.total, "Total items", "total"),
    statCard(totals.backlog, "Backlog", "backlog"),
    statCard(totals.in_progress, "In progress", "in_progress"),
    statCard(totals.blocked, "Blocked", "blocked"),
    statCard(totals.done, `Done · last ${days} days`, "done"),
  );
  const tree = filterTree(portfolioTree(cards, groupBy, role), text);
  const organizations = new Set(
    cards.flatMap((card) => card.organizations.map((entry) => entry.org)),
  );
  const projects = new Set(cards.map((card) => card.project).filter((key) => key !== null));
  const panel = el("section", "panel");
  const head = el("header", "panel-head");
  const heading = el(
    "h2",
    "",
    groupBy === "organization" ? "Projects by organization" : "Repositories by project",
  );
  head.append(
    heading,
    el(
      "span",
      "muted",
      `${formatCount(organizations.size)} organizations · ${formatCount(projects.size)} projects`,
    ),
    el("span", "muted panel-sort", "Sorted by total, largest first"),
  );
  const table = el("div", "ptable");
  table.setAttribute("role", "table");
  const columns = el("div", "prow prow-head");
  columns.setAttribute("role", "row");
  const first = groupBy === "organization" ? "Organization / project" : "Project / repository";
  for (const label of [first, "Total", "Backlog", "In progress", "Blocked", `Done ${days}d`, ""]) {
    columns.append(el("span", "num", label));
  }
  table.append(columns);
  for (const row of tree) {
    const closed = collapsed.has(row.key);
    table.append(
      portfolioGroupRow(row, closed, groupBy, () => {
        if (closed) {
          collapsed.delete(row.key);
        } else {
          collapsed.add(row.key);
        }
        requestRender();
      }),
    );
    if (!closed) {
      for (const child of row.children) {
        table.append(
          portfolioChildRow(child, (blocked) => {
            const target = blocked ? { view: "blocked", column: "" } : portfolioTarget(state);
            applyFilter(child.filter, target.view, target.column);
          }),
        );
      }
    }
  }
  if (tree.length === 0) {
    table.append(el("p", "empty", "Nothing matches."));
  }
  panel.append(head, table);
  store.navKeys = [];
  content.replaceChildren(stats, panel);
}
