import { requestRender } from "./request-render.js";
import { store } from "./store.js";

// Hide the detail panel and return focus to the selected card.
export function closeDetail() {
  if (!store.detail) {
    return;
  }
  store.detail = false;
  requestRender();
  window.requestAnimationFrame(() => {
    const key = store.selected;
    const card = [...document.querySelectorAll("[data-key]")].find((n) => n.dataset.key === key);
    card?.focus();
  });
}
