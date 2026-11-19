import { capitalize } from "./capitalize.js";
import { fillSelect } from "./fill-select.js";
import { isPhone } from "./is-phone.js";
import { ownView } from "./own-view.js";
import { sortChoices } from "./sort-choices.js";

// Bring the static controls in line with the store: the filter count, the
// Display popover (group, sort, the done window, empty columns, cancelled
// items) and its summary, the layout, and the portfolio toolbar.
export function renderToolbar(store) {
  const portfolio = store.view === "portfolio";
  const board = store.view === "board" && !isPhone();
  document.getElementById("toolbar").hidden = portfolio || ownView(store.view);
  document.getElementById("portfolio-toolbar").hidden = !portfolio;
  const count = store.filters.rules.length + (store.filters.waitingOnMe ? 1 : 0);
  const badge = document.getElementById("filters-count");
  badge.hidden = count === 0;
  badge.textContent = String(count);
  const companies = (store.index?.companies.length ?? 0) > 0;
  const groups = [
    ["state", "State"],
    ...(companies ? [["company", "Company"], ["project", "Project"]] : []),
    ["repository", "Repository"],
    ["priority", "Priority"],
    ["kind", "Kind"],
    ["assignee", "Assignee"],
    ...(store.view === "done" ? [["day", "Closing day"]] : []),
  ];
  const group = document.getElementById("group");
  fillSelect(group, board ? [["state", "State"]] : groups, board ? "state" : store.group);
  group.disabled = board;
  const sort = document.getElementById("sort");
  const sorts = sortChoices(store.view);
  fillSelect(sort, sorts, store.sort);
  const days = store.payload?.done_days ?? 14;
  const windows = [...new Set([7, 14, 30, 90, 365, days])].sort((a, b) => a - b);
  fillSelect(
    document.getElementById("done-days"),
    windows.map((count) => [String(count), `${count} days`]),
    String(days),
  );
  document.getElementById("show-empty").checked = store.showEmpty;
  document.getElementById("filter-showCancelled").checked = store.filters.showCancelled;
  const groupTitle = groups.find(([value]) => value === group.value)?.[1] ?? "State";
  const sortTitle = sorts.find(([value]) => value === sort.value)?.[1] ?? "";
  document.getElementById("display-summary").textContent = board ? sortTitle : `${groupTitle} · ${sortTitle}`;
  document.getElementById("layout-list").setAttribute("aria-pressed", String(!board));
  document
    .getElementById("layout-board")
    .setAttribute("aria-pressed", String(store.view === "board"));
  const relations = (store.index?.roles ?? []).map((role) => [
    `role:${role}`,
    capitalize(role),
  ]);
  fillSelect(
    document.getElementById("portfolio-group"),
    [[companies ? "company" : "repository", companies ? "Company" : "Repository"], ...relations],
    store.portfolio.groupBy,
  );
  document.getElementById("portfolio-state").value = store.portfolio.state;
}
