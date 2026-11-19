import { COLUMN_TITLES } from "./column-titles.js";
import { el } from "./el.js";
import { formatClock } from "./format-clock.js";
import { formatCount } from "./format-count.js";
import { ownView } from "./own-view.js";
import { placesCounts } from "./places-counts.js";
import { placesLabel } from "./places-label.js";
import { plural } from "./plural.js";
import { stateRule } from "./state-rule.js";
import { VIEW_TITLES } from "./view-titles.js";

// Page title with the chosen places ("Board — Pixel Potion, Globex CRM")
// and a subtitle of what they hold ("12 projects · 2,405 items"), the update time or error,
// and the scan problems.
export function renderHead(store, sets) {
  const payload = store.payload;
  const view = VIEW_TITLES.find(([key]) => key === store.view)?.[1] ?? "Board";
  const state = stateRule(store.filters);
  const one = state?.op === "any" && state.values.length === 1 ? state.values[0] : "";
  const named = store.view === "all" && one !== "" ? `${view}: ${COLUMN_TITLES[one] ?? one}` : view;
  const scope = store.index ? placesLabel(store.places, store.index, "") : "";
  const title = scope === "" ? named : `${named} — ${scope}`;
  document.getElementById("page-title").textContent = title;
  document.title = `${title} · tadu`;
  const cards = store.cards;
  const total = sets.total;
  const filtered = sets.shown.length !== total;
  const items = filtered
    ? `${formatCount(sets.shown.length)} shown of ${plural(total, "item")}`
    : plural(total, "item");
  // A view that draws its own page (Changes, Next...) counts its own rows; the scope's count
  // of items would not be what it shows.
  const counts = ownView(store.view) ? [] : [items];
  document.getElementById("page-subtitle").textContent = payload
    ? [...placesCounts(store.places, store.index), ...counts].join(" · ")
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
