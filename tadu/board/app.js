import { applyTheme } from "./apply-theme.js";
import { bindControls } from "./bind-controls.js";
import { bindKeys } from "./bind-keys.js";
import { bindPicker } from "./bind-picker.js";
import { cleanWhere } from "./clean-where.js";
import { fillIcons } from "./fill-icons.js";
import { loadBoard } from "./load-board.js";
import { openDetail } from "./open-detail.js";
import { parseHash } from "./parse-hash.js";
import { renderApp } from "./render-app.js";
import { renderListWindow } from "./render-list-window.js";
import { requestRender } from "./request-render.js";
import { store } from "./store.js";
import { storedTheme } from "./stored-theme.js";
import { VIEW_TITLES } from "./view-titles.js";

// Entry point of the tadu board page: renders /api/cards, read only. Every
// piece of backlog text reaches the page through textContent or text nodes.
export function start() {
  const views = VIEW_TITLES.map(([view]) => view);
  store.hash = parseHash(window.location.hash);
  if (views.includes(store.hash.view)) {
    store.view = store.hash.view;
  }
  store.theme = storedTheme();
  applyTheme(store.theme);
  const mac = /Mac|iPhone|iPad/.test(navigator.platform);
  document.getElementById("search-key").textContent = mac ? "⌘ K" : "Ctrl K";
  fillIcons(document);
  bindControls(store);
  bindKeys(store);
  bindPicker(store);
  window.addEventListener("hashchange", () => {
    const hash = parseHash(window.location.hash);
    if (store.index && hash.given) {
      store.where = cleanWhere(hash.where, store.index);
      store.view = views.includes(hash.view) ? hash.view : store.view;
      requestRender();
    }
  });
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
