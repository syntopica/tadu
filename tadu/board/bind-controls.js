import { commitChoice } from "./commit-choice.js";
import { DEFAULT_FILTERS } from "./default-filters.js";
import { EMPTY_WHERE } from "./empty-where.js";
import { debounce } from "./debounce.js";
import { applyTheme } from "./apply-theme.js";
import { loadBoard } from "./load-board.js";
import { nextTheme } from "./next-theme.js";
import { requestRender } from "./request-render.js";
import { SEARCHABLE_FILTERS } from "./searchable-filters.js";
import { setView } from "./set-view.js";
import { setWhere } from "./set-where.js";
import { snapshotView } from "./snapshot-view.js";
import { storageKey } from "./storage-key.js";
import { storeSavedViews } from "./store-saved-views.js";
import { toggleFavourite } from "./toggle-favourite.js";
import { togglePopover } from "./toggle-popover.js";
import { writeStored } from "./write-stored.js";

// Wire the static controls of index.html to the store.
export function bindControls(store) {
  const byId = (id) => document.getElementById(id);
  const search = debounce((value) => {
    store.text = value;
    requestRender();
  }, 120);
  byId("search").addEventListener("input", (event) =>
    search(event.target.value),
  );
  const portfolioSearch = debounce((value) => {
    store.portfolio.text = value;
    requestRender();
  }, 120);
  byId("portfolio-search").addEventListener("input", (event) =>
    portfolioSearch(event.target.value),
  );
  byId("phone-search").addEventListener("click", () =>
    byId(store.view === "portfolio" ? "portfolio-search" : "search").focus(),
  );
  for (const name of ["role", "priority", "column", "dueBefore"]) {
    byId(`filter-${name}`).addEventListener("change", (event) => {
      store.filters = { ...store.filters, [name]: event.target.value };
      requestRender();
    });
  }
  for (const name of SEARCHABLE_FILTERS) {
    const input = byId(`filter-${name}`);
    input.addEventListener("input", () => commitChoice(name, input, false));
    input.addEventListener("change", () => commitChoice(name, input, true));
  }
  for (const name of [
    "unassigned",
    "noPriority",
    "waitingOnMe",
    "showCancelled",
  ]) {
    byId(`filter-${name}`).addEventListener("change", (event) => {
      store.filters = { ...store.filters, [name]: event.target.checked };
      requestRender();
    });
  }
  byId("show-empty").addEventListener("change", (event) => {
    store.showEmpty = event.target.checked;
    requestRender();
  });
  byId("filters-button").addEventListener("click", () =>
    togglePopover(byId("filters-popover").hidden),
  );
  document.addEventListener("click", (event) => {
    if (!event.target.closest?.(".popover-anchor, #picker")) {
      togglePopover(false);
    }
  });
  byId("group").addEventListener("change", (event) => {
    store.group = event.target.value;
    store.collapsed = new Set();
    requestRender();
  });
  byId("sort").addEventListener("change", (event) => {
    store.sort = event.target.value;
    requestRender();
  });
  byId("layout-list").addEventListener(
    "click",
    () => store.view === "board" && setView("all"),
  );
  byId("layout-board").addEventListener(
    "click",
    () => store.view !== "board" && setView("board"),
  );
  byId("portfolio-group").addEventListener("change", (event) => {
    store.portfolio.groupBy = event.target.value;
    store.portfolio.collapsed = new Set();
    store.portfolio.expanded = new Set();
    requestRender();
  });
  byId("clear-all").addEventListener("click", () => {
    store.filters = { ...DEFAULT_FILTERS };
    store.showEmpty = false;
    setWhere(EMPTY_WHERE);
  });
  byId("favourite").addEventListener("click", () => {
    store.favourites = toggleFavourite(store.favourites, store.where);
    writeStored(storageKey("favourites", store.payload.workspace_id), store.favourites);
    requestRender();
  });
  byId("portfolio-state").addEventListener("change", (event) => {
    store.portfolio.state = event.target.value;
    requestRender();
  });
  for (const id of ["reload", "reload-phone"]) {
    byId(id).addEventListener("click", loadBoard);
  }
  byId("problems-button").addEventListener("click", () => {
    store.problemsOpen = !store.problemsOpen;
    requestRender();
  });
  byId("theme-toggle").addEventListener("click", () => {
    store.theme = nextTheme(store.theme);
    applyTheme(store.theme);
    requestRender();
  });
  byId("save-view-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const name = byId("save-view-name").value.trim();
    if (name === "" || !store.payload) {
      return;
    }
    store.saved = [
      ...store.saved.filter((saved) => saved.name !== name),
      snapshotView(name),
    ];
    storeSavedViews(store.saved, store.payload.workspace_id);
    byId("save-view-name").value = "";
    requestRender();
  });
}
