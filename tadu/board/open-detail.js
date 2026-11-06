import { requestRender } from "./request-render.js";
import { store } from "./store.js";

// Select a card and show it in the detail panel.
export function openDetail(key) {
  store.selected = key;
  store.detail = true;
  store.focusDetail = true;
  requestRender();
}
