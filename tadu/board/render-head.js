import { COLUMN_TITLES } from "./column-titles.js";
import { el } from "./el.js";
import { formatClock } from "./format-clock.js";
import { formatCount } from "./format-count.js";
import { plural } from "./plural.js";
import { VIEW_TITLES } from "./view-titles.js";

// Page title and subtitle, the update time or error, and the scan problems.
export function renderHead(store, sets) {
  const payload = store.payload;
  const title = VIEW_TITLES.find(([view]) => view === store.view)?.[1] ?? "Board";
  const column = store.filters.column;
  document.getElementById("page-title").textContent =
    store.view === "all" && column !== "" ? `${title}: ${COLUMN_TITLES[column]}` : title;
  document.title = `${title} · tadu`;
  const cards = store.cards;
  const repositories = plural(new Set(cards.map((card) => card.repository)).size, "repository");
  const total = sets.total;
  const filtered = sets.shown.length !== total && store.view !== "portfolio";
  const items = filtered
    ? `${formatCount(sets.shown.length)} shown of ${plural(total, "item")}`
    : plural(total, "item");
  document.getElementById("page-subtitle").textContent = payload
    ? `${repositories} · ${items}`
    : "";
  const updated = store.loading
    ? "Reloading..."
    : store.error || (payload ? `Updated ${formatClock(payload.generated_at)}` : "Loading...");
  for (const id of ["updated", "updated-phone"]) {
    const node = document.getElementById(id);
    node.textContent = updated;
    node.classList.toggle("error", store.error !== "" && !store.loading);
  }
  const problems = payload?.problems ?? [];
  const warned = cards.filter((card) => card.problems.length > 0).length;
  const button = document.getElementById("problems-button");
  button.hidden = problems.length + warned === 0;
  button.setAttribute("aria-expanded", String(store.problemsOpen));
  document.getElementById("problems-label").textContent = plural(
    problems.length + warned,
    "integrity notice",
  );
  const panel = document.getElementById("problems-panel");
  panel.hidden = !store.problemsOpen || button.hidden;
  panel.replaceChildren(
    el("h2", "", "Integrity notices"),
    el(
      "p",
      "muted",
      `${plural(problems.length, "scan problem")} · ${plural(warned, "item")} with parse warnings`,
    ),
    ...problems.map((problem) =>
      el("p", "notice-line", `${problem.repository}: ${problem.message}`),
    ),
  );
}
