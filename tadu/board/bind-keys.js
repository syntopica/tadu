import { closeDetail } from "./close-detail.js";
import { nextKey } from "./next-key.js";
import { openDetail } from "./open-detail.js";
import { openEditor } from "./open-editor.js";
import { requestRender } from "./request-render.js";
import { revealKey } from "./reveal-key.js";
import { togglePopover } from "./toggle-popover.js";
import { typingTarget } from "./typing-target.js";

// Keyboard: "/" and Cmd/Ctrl-K search, J/K move, Enter opens the detail,
// E opens the editor, Esc closes popovers and the detail.
export function bindKeys(store) {
  document.addEventListener("keydown", (event) => {
    const searchId = store.view === "portfolio" ? "portfolio-search" : "search";
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      document.getElementById(searchId).focus();
      return;
    }
    if (event.key === "Escape") {
      if (!document.getElementById("filters-popover").hidden) {
        togglePopover(false);
        document.getElementById("filters-button").focus();
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
    if (typingTarget(event.target) || event.metaKey || event.ctrlKey || event.altKey) {
      return;
    }
    const key = event.key.toLowerCase();
    if (event.key === "/") {
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
    } else if (event.key === "Enter" && store.selected && !event.target.closest?.("button, a")) {
      openDetail(store.selected);
    } else if (key === "e") {
      openEditor(store.byKey.get(store.selected));
    }
  });
}
