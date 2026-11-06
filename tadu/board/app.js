import { applyTheme } from "./apply-theme.js";
import { bindControls } from "./bind-controls.js";
import { bindKeys } from "./bind-keys.js";
import { fillIcons } from "./fill-icons.js";
import { loadBoard } from "./load-board.js";
import { loadSavedViews } from "./load-saved-views.js";
import { openDetail } from "./open-detail.js";
import { renderApp } from "./render-app.js";
import { renderListWindow } from "./render-list-window.js";
import { requestRender } from "./request-render.js";
import { store } from "./store.js";
import { storedTheme } from "./stored-theme.js";

// Entry point of the tadu board page: renders /api/cards, read only. Every
// piece of backlog text reaches the page through textContent or text nodes.
export function start() {
  store.theme = storedTheme();
  applyTheme(store.theme);
  store.saved = loadSavedViews();
  const mac = /Mac|iPhone|iPad/.test(navigator.platform);
  document.getElementById("search-key").textContent = mac ? "⌘ K" : "Ctrl K";
  fillIcons(document);
  bindControls(store);
  bindKeys(store);
  document.getElementById("content").addEventListener("click", (event) => {
    const item = event.target.closest?.("[data-key]");
    if (item) {
      openDetail(item.dataset.key);
    }
  });
  window.addEventListener("tadu:render", () => renderApp(store));
  window.addEventListener("scroll", () => store.list && renderListWindow(store, store.list), {
    passive: true,
  });
  window.addEventListener("resize", requestRender);
  requestRender();
  loadBoard();
}

start();
