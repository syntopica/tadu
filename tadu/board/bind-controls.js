import { applyTheme } from "./apply-theme.js";
import { applyTypedFilters } from "./apply-typed-filters.js";
import { closeFilterMenu } from "./close-filter-menu.js";
import { closePopovers } from "./close-popovers.js";
import { debounce } from "./debounce.js";
import { itemFilterSource } from "./item-filter-source.js";
import { loadBoard } from "./load-board.js";
import { newItemSpec } from "./new-item-spec.js";
import { nextTheme } from "./next-theme.js";
import { openChange } from "./open-change.js";
import { openFilterMenu } from "./open-filter-menu.js";
import { requestRender } from "./request-render.js";
import { setView } from "./set-view.js";
import { signOut } from "./sign-out.js";
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
  const searchBox = byId("search");
  searchBox.addEventListener("input", () => {
    if (applyTypedFilters(store, searchBox, false)) {
      requestRender();
    }
    search(searchBox.value);
  });
  searchBox.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && applyTypedFilters(store, searchBox, true)) {
      search(searchBox.value);
      requestRender();
    }
  });
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
  byId("filter-showCancelled").addEventListener("change", (event) => {
    store.filters = { ...store.filters, showCancelled: event.target.checked };
    requestRender();
  });
  const filterAdd = byId("filter-add");
  filterAdd.dataset.filterAnchor = "";
  filterAdd.addEventListener("click", () => {
    if (store.menu?.anchor === filterAdd) {
      closeFilterMenu(true);
    } else if (store.payload) {
      openFilterMenu(itemFilterSource(store), filterAdd);
    }
  });
  byId("done-days").addEventListener("change", (event) => {
    store.doneDays = Number(event.target.value);
    loadBoard();
  });
  byId("new-item").addEventListener("click", () => {
    const spec = newItemSpec(store.payload, store.places, store.index);
    if (spec !== null) {
      openChange(store, spec, byId("new-item"));
    }
  });
  byId("show-empty").addEventListener("change", (event) => {
    store.showEmpty = event.target.checked;
    requestRender();
  });
  byId("display-button").addEventListener("click", () =>
    togglePopover(byId("display-popover").hidden),
  );
  document.addEventListener("click", (event) => {
    if (event.target.isConnected !== false) {
      closePopovers(event.target.closest?.(".popover-anchor") ?? null);
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
  byId("favourite").addEventListener("click", () => {
    store.favourites = toggleFavourite(store.favourites, store.places);
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
  byId("sign-out").addEventListener("click", signOut);
  byId("session-sign-out").addEventListener("click", signOut);
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
