import { closeDetail } from "./close-detail.js";
import { closeFilterMenu } from "./close-filter-menu.js";
import { closePicker } from "./close-picker.js";
import { closePopovers } from "./close-popovers.js";
import { itemFilterSource } from "./item-filter-source.js";
import { nextKey } from "./next-key.js";
import { openDetail } from "./open-detail.js";
import { openEditor } from "./open-editor.js";
import { openFilterMenu } from "./open-filter-menu.js";
import { openPicker } from "./open-picker.js";
import { requestRender } from "./request-render.js";
import { revealKey } from "./reveal-key.js";
import { typingTarget } from "./typing-target.js";

// Keyboard: "/" and Cmd/Ctrl-K search, F opens the Filter menu, G then S
// opens the scope switcher, J/K move, Enter opens the detail, E opens the
// editor, Esc closes the change dialog, menus, pickers, popovers and the
// detail. While the change dialog is open, the other keys are left to it.
export function bindKeys(store) {
  let pressedG = 0;
  document.addEventListener("keydown", (event) => {
    const searchId = store.view === "portfolio" ? "portfolio-search" : "search";
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      document.getElementById(searchId).focus();
      return;
    }
    if (event.key === "Escape") {
      if (store.change !== null) {
        store.change = null;
        requestRender();
      } else if (store.menu !== null) {
        closeFilterMenu(true);
      } else if (store.picker !== null) {
        closePicker(true);
      } else if (document.querySelector(".popover:not([hidden])")) {
        const open = document.querySelector(".popover:not([hidden])");
        closePopovers();
        open.closest(".popover-anchor")?.querySelector("[aria-expanded]")?.focus();
      } else if (store.navOpen) {
        store.navOpen = false;
        requestRender();
      } else if (typingTarget(event.target)) {
        event.target.blur();
      } else {
        closeDetail();
      }
      return;
    }
    if (
      store.change !== null ||
      typingTarget(event.target) ||
      event.metaKey ||
      event.ctrlKey ||
      event.altKey
    ) {
      return;
    }
    const key = event.key.toLowerCase();
    const afterG = Date.now() - pressedG < 1000;
    pressedG = key === "g" ? Date.now() : 0;
    if (key === "s" && afterG) {
      event.preventDefault();
      openPicker(null);
    } else if (key === "f" && !document.getElementById("toolbar").hidden && store.payload) {
      event.preventDefault();
      openFilterMenu(itemFilterSource(store), document.getElementById("filter-add"));
    } else if (event.key === "/") {
      event.preventDefault();
      document.getElementById(searchId).focus();
    } else if (key === "j" || key === "k") {
      const next = nextKey(store.navKeys, store.selected, key === "j" ? 1 : -1);
      if (next !== null) {
        store.selected = next;
        requestRender();
        window.requestAnimationFrame(() =>
          window.requestAnimationFrame(() => revealKey(store, next)),
        );
      }
    } else if (event.key === "Enter" && store.selected && !event.target.closest?.('button, a, [role="button"]')) {
      openDetail(store.selected);
    } else if (key === "e") {
      openEditor(store.byKey.get(store.selected));
    }
  });
}
