import { companyCard } from "./company-card.js";
import { companyTree } from "./company-tree.js";
import { el } from "./el.js";
import { filterTree } from "./filter-tree.js";
import { isPhone } from "./is-phone.js";
import { plural } from "./plural.js";
import { portfolioCards } from "./portfolio-cards.js";
import { portfolioDrill } from "./portfolio-drill.js";
import { portfolioRow } from "./portfolio-row.js";
import { relationTree } from "./relation-tree.js";
import { requestRender } from "./request-render.js";
import { statCard } from "./stat-card.js";
import { treeTotals } from "./tree-totals.js";
import { whereCounts } from "./where-counts.js";

// Stat cards and the tree of the scope: Company > Project > Repository by
// ownership, or a relation's organizations over their projects; on a phone,
// one card per company. Companies start open, projects folded.
export function renderPortfolio(store, content) {
  const { groupBy, state, text, collapsed, expanded } = store.portfolio;
  const index = store.index;
  const cards = portfolioCards(store.cards, state, store.where);
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
  const role = groupBy.startsWith("role:") ? groupBy.slice(5) : "";
  const keepEmpty = state === "";
  const rows = filterTree(
    role !== "" && index.roles.includes(role)
      ? relationTree(cards, index, store.where, role, keepEmpty)
      : companyTree(cards, index, store.where, keepEmpty),
    text,
  );
  const flip = (set, key) => () => {
    if (!set.delete(key)) {
      set.add(key);
    }
    requestRender();
  };
  const drill = (node) => portfolioDrill(node, state);
  store.navKeys = [];
  if (isPhone()) {
    const groups =
      rows.length > 0 && rows[0].kind === "repository"
        ? [{ kind: "company", label: "Repositories", children: rows, buckets: totals, projects: 0, repositories: rows.length, relations: [] }]
        : rows;
    content.replaceChildren(
      stats,
      ...groups.map((group) =>
        companyCard(group, expanded.has(`all:${group.key}`), drill, flip(expanded, `all:${group.key}`)),
      ),
      ...(groups.length === 0 ? [el("p", "empty-state", "Nothing matches.")] : []),
    );
    return;
  }
  const panel = el("section", "panel");
  const head = el("header", "panel-head");
  const structured = index.companies.length > 0;
  const heading = role !== "" ? `Projects by ${role}` : structured ? "Companies" : "Repositories";
  head.append(
    el("h2", "", heading),
    el("span", "muted", [...whereCounts(store.where, index), plural(totals.total, "item")].join(" · ")),
    el("span", "muted panel-sort", "Sorted by total, largest first"),
  );
  const table = el("div", "ptable");
  table.setAttribute("role", "table");
  const columns = el("div", "prow prow-head");
  columns.setAttribute("role", "row");
  const first = role !== "" ? `${role} / project / repository` : structured ? "Company / project / repository" : "Repository";
  for (const label of [first, "Total", "Backlog", "In progress", "Blocked", `Done ${days}d`, ""]) {
    columns.append(el("span", "num", label));
  }
  table.append(columns);
  const searching = text.trim() !== "";
  const walk = (node, depth) => {
    const open =
      depth === 0
        ? !collapsed.has(node.key)
        : searching || store.where.project !== "" || expanded.has(node.key);
    const set = depth === 0 ? collapsed : expanded;
    table.append(portfolioRow(node, depth, { open, onToggle: flip(set, node.key), onOpen: drill(node) }));
    if (open) {
      node.children.forEach((child) => walk(child, depth + 1));
    }
  };
  rows.forEach((row) => walk(row, 0));
  if (rows.length === 0) {
    table.append(el("p", "empty", "Nothing matches."));
  }
  panel.append(head, table);
  content.replaceChildren(stats, panel);
}
