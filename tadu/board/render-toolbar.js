import { activeChips } from "./active-chips.js";
import { COLUMN_TITLES } from "./column-titles.js";
import { distinctValues } from "./distinct-values.js";
import { fillChoice } from "./fill-choice.js";
import { fillSelect } from "./fill-select.js";
import { isPhone } from "./is-phone.js";
import { PRIORITY_TITLES } from "./priority-titles.js";
import { SEARCHABLE_FILTERS } from "./searchable-filters.js";

// Bring the static controls in line with the store: filters, group, sort,
// layout and the portfolio toolbar.
export function renderToolbar(store) {
  const cards = store.cards;
  const names = store.index?.orgNames ?? new Map();
  const portfolio = store.view === "portfolio";
  const board = store.view === "board" && !isPhone();
  document.getElementById("toolbar").hidden = portfolio;
  document.getElementById("portfolio-toolbar").hidden = !portfolio;
  for (const name of SEARCHABLE_FILTERS) {
    fillChoice(
      document.getElementById(`filter-${name}`),
      distinctValues(cards, name),
      store.filters[name],
      name === "organization" ? names : undefined,
    );
  }
  fillSelect(
    document.getElementById("filter-role"),
    [["", "Any"], ...distinctValues(cards, "role").map((value) => [value, value])],
    store.filters.role,
  );
  fillSelect(
    document.getElementById("filter-priority"),
    [["", "Any"], ...Object.entries(PRIORITY_TITLES)],
    store.filters.priority,
  );
  const columns = (store.payload?.columns ?? []).map((column) => [column, COLUMN_TITLES[column]]);
  fillSelect(document.getElementById("filter-column"), [["", "Any"], ...columns], store.filters.column);
  document.getElementById("filter-dueBefore").value = store.filters.dueBefore;
  for (const name of ["unassigned", "noPriority", "waitingOnMe", "showCancelled"]) {
    document.getElementById(`filter-${name}`).checked = store.filters[name];
  }
  document.getElementById("filter-waitingOnMe").disabled = !store.payload?.me;
  document.getElementById("show-empty").checked = store.showEmpty;
  const count = activeChips(store.filters, names).filter((chip) => chip.name !== "column").length;
  const badge = document.getElementById("filters-count");
  badge.hidden = count === 0;
  badge.textContent = String(count);
  const companies = (store.index?.companies.length ?? 0) > 0;
  const groups = [
    ["state", "State"],
    ...(companies ? [["company", "Company"], ["project", "Project"]] : []),
    ["repository", "Repository"],
    ["priority", "Priority"],
    ["assignee", "Assignee"],
    ...(store.view === "done" ? [["day", "Closing day"]] : []),
  ];
  fillSelect(
    document.getElementById("group"),
    board ? [["state", "State"]] : groups,
    board ? "state" : store.group,
  );
  document.getElementById("group").disabled = board;
  const sorts = [
    ["priority", "Priority"],
    ["due", "Due date"],
    ["title", "Title"],
    ["location", "Location"],
    ...(store.view === "done" ? [["closed", "Closing day"]] : []),
  ];
  fillSelect(document.getElementById("sort"), sorts, store.sort);
  document.getElementById("layout-list").setAttribute("aria-pressed", String(!board));
  document
    .getElementById("layout-board")
    .setAttribute("aria-pressed", String(store.view === "board"));
  const relations = (store.index?.roles ?? []).map((role) => [
    `role:${role}`,
    `${role[0].toUpperCase()}${role.slice(1)}`,
  ]);
  fillSelect(
    document.getElementById("portfolio-group"),
    [[companies ? "company" : "repository", companies ? "Company" : "Repository"], ...relations],
    store.portfolio.groupBy,
  );
  document.getElementById("portfolio-state").value = store.portfolio.state;
}
