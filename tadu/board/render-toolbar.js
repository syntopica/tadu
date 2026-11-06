import { activeChips } from "./active-chips.js";
import { distinctValues } from "./distinct-values.js";
import { fillSelect } from "./fill-select.js";
import { isPhone } from "./is-phone.js";
import { PRIORITY_TITLES } from "./priority-titles.js";

// Bring the static controls in line with the store: scope, filters, group,
// sort, layout and the portfolio toolbar.
export function renderToolbar(store) {
  const cards = store.cards;
  const portfolio = store.view === "portfolio";
  const board = store.view === "board" && !isPhone();
  document.getElementById("toolbar").hidden = portfolio;
  document.getElementById("portfolio-toolbar").hidden = !portfolio;
  const projects = distinctValues(cards, "project").map((key) => [key, key]);
  fillSelect(
    document.getElementById("scope-project"),
    [["", "All projects"], ...projects],
    store.filters.project,
  );
  for (const name of ["repository", "organization", "role", "assignee", "label"]) {
    const values = distinctValues(cards, name).map((value) => [value, value]);
    fillSelect(
      document.getElementById(`filter-${name}`),
      [["", "Any"], ...values],
      store.filters[name],
    );
  }
  const priorities = Object.entries(PRIORITY_TITLES);
  fillSelect(
    document.getElementById("filter-priority"),
    [["", "Any"], ...priorities],
    store.filters.priority,
  );
  for (const name of ["unassigned", "noPriority", "waitingOnMe", "showCancelled"]) {
    document.getElementById(`filter-${name}`).checked = store.filters[name];
  }
  document.getElementById("filter-waitingOnMe").disabled = !store.payload?.me;
  document.getElementById("show-empty").checked = store.showEmpty;
  const count = activeChips(store.filters).filter((chip) => chip.name !== "column").length;
  const badge = document.getElementById("filters-count");
  badge.hidden = count === 0;
  badge.textContent = String(count);
  const groups = [
    ["state", "State"],
    ["project", "Project"],
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
  const roles = distinctValues(cards, "role").map((role) => [role, role]);
  fillSelect(
    document.getElementById("portfolio-role"),
    [["", "All"], ...roles],
    store.portfolio.role,
  );
  document.getElementById("portfolio-group").value = store.portfolio.groupBy;
  document.getElementById("portfolio-state").value = store.portfolio.state;
}
