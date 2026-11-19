import { closeFilterMenu } from "./close-filter-menu.js";
import { renderFilterMenu } from "./render-filter-menu.js";
import { store } from "./store.js";

// Open the Filter menu under `anchor` for `source` (what it filters: its
// fields and values, quick filters, rules and how to change them), on its
// first step, or straight on `field`'s step (a chip being edited).
export function openFilterMenu(source, anchor, field = null) {
  closeFilterMenu(false);
  store.menu = { source, anchor, field, direct: field !== null, op: null, active: 0, options: [] };
  const menu = document.getElementById("filter-menu");
  const rect = anchor.getBoundingClientRect();
  const left = Math.max(8, Math.min(rect.left, window.innerWidth - 328));
  menu.style.setProperty("--menu-top", `${Math.round(rect.bottom + 6)}px`);
  menu.style.setProperty("--menu-left", `${Math.round(left)}px`);
  anchor.setAttribute("aria-expanded", "true");
  const input = document.getElementById("filter-menu-input");
  input.value = "";
  menu.hidden = false;
  renderFilterMenu(store);
  input.focus();
}
