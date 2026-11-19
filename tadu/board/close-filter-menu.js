import { store } from "./store.js";

// Close the Filter menu; `refocus` returns the focus to the control that
// opened it, when that control is still on the page.
export function closeFilterMenu(refocus) {
  const menu = store.menu;
  if (menu === null) {
    return;
  }
  store.menu = null;
  document.getElementById("filter-menu").hidden = true;
  menu.anchor?.setAttribute("aria-expanded", "false");
  if (refocus && menu.anchor?.isConnected) {
    menu.anchor.focus();
  }
}
