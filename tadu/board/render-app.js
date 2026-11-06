import { currentSets } from "./current-sets.js";
import { el } from "./el.js";
import { isPhone } from "./is-phone.js";
import { renderBoard } from "./render-board.js";
import { renderBottomNav } from "./render-bottom-nav.js";
import { renderChips } from "./render-chips.js";
import { renderDetail } from "./render-detail.js";
import { renderHead } from "./render-head.js";
import { renderList } from "./render-list.js";
import { renderListHead } from "./render-list-head.js";
import { renderPortfolio } from "./render-portfolio.js";
import { renderScopeBar } from "./render-scope-bar.js";
import { renderSidebar } from "./render-sidebar.js";
import { renderSummary } from "./render-summary.js";
import { renderToolbar } from "./render-toolbar.js";
import { syncLocation } from "./sync-location.js";

// Draw the whole page from the store.
export function renderApp(store) {
  const sets = currentSets(store);
  document.body.dataset.view = store.view;
  renderSidebar(store);
  renderScopeBar(store);
  renderHead(store, sets);
  renderToolbar(store);
  renderChips(store);
  renderSummary(store, sets);
  renderListHead(store, sets);
  renderBottomNav(store);
  const content = document.getElementById("content");
  if (!store.payload) {
    store.list = null;
    content.replaceChildren(el("p", "empty-state", store.error || "Loading the workspace..."));
  } else if (store.view === "portfolio") {
    store.list = null;
    renderPortfolio(store, content);
  } else if (store.view === "board" && !isPhone()) {
    store.list = null;
    renderBoard(store, sets, content);
  } else {
    renderList(store, sets, content);
  }
  renderDetail(store);
  syncLocation(store);
}
