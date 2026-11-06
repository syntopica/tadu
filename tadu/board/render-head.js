import { COLUMN_TITLES } from "./column-titles.js";
import { el } from "./el.js";
import { formatClock } from "./format-clock.js";
import { formatCount } from "./format-count.js";
import { plural } from "./plural.js";
import { VIEW_TITLES } from "./view-titles.js";
import { whereCounts } from "./where-counts.js";
import { whereParts } from "./where-parts.js";

// Page title with the scope ("Board — Pixel Potion") and a subtitle of what
// the scope holds ("12 projects · 2,405 items"), the update time or error,
// and the scan problems.
export function renderHead(store, sets) {
  const payload = store.payload;
  const view = VIEW_TITLES.find(([key]) => key === store.view)?.[1] ?? "Board";
  const column = store.filters.column;
  const named = store.view === "all" && column !== "" ? `${view}: ${COLUMN_TITLES[column]}` : view;
  const scope = store.index ? whereParts(store.where, store.index).at(-1)?.label : undefined;
  const title = scope === undefined ? named : `${named} — ${scope}`;
  document.getElementById("page-title").textContent = title;
  document.title = `${title} · tadu`;
  const cards = store.cards;
  const total = sets.total;
  const filtered = sets.shown.length !== total;
  const items = filtered
    ? `${formatCount(sets.shown.length)} shown of ${plural(total, "item")}`
    : plural(total, "item");
  document.getElementById("page-subtitle").textContent = payload
    ? [...whereCounts(store.where, store.index), items].join(" · ")
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
