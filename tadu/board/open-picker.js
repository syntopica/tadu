import { placeState } from "./place-state.js";
import { renderPicker } from "./render-picker.js";
import { scopeNodes } from "./scope-nodes.js";
import { store } from "./store.js";

// Open the scope picker under the control that asked for it, or as the
// keyboard switcher (G S, no anchor) near the top of the page. The tree
// starts unfolded down to what is chosen, and fully when it is small.
export function openPicker(anchor) {
  if (!store.index) {
    return;
  }
  store.picker?.anchor?.setAttribute("aria-expanded", "false");
  const open = new Set();
  const nodes = scopeNodes(store.index);
  const small = nodes.reduce((sum, node) => sum + 1 + node.children.length, 0) <= 24;
  const unfold = (list) => {
    for (const node of list) {
      if (node.children.length > 0 && (small || placeState(node.place, store.places, store.index) === "mixed")) {
        open.add(node.key);
        unfold(node.children);
      }
    }
  };
  unfold(nodes);
  store.picker = { anchor, open, active: 0, rows: [], ticked: false };
  const picker = document.getElementById("picker");
  const input = document.getElementById("picker-input");
  input.value = "";
  picker.classList.toggle("switcher", anchor === null);
  if (anchor !== null) {
    const rect = anchor.getBoundingClientRect();
    const left = Math.max(8, Math.min(rect.left, window.innerWidth - 408));
    picker.style.setProperty("--picker-top", `${Math.round(rect.bottom + 6)}px`);
    picker.style.setProperty("--picker-left", `${Math.round(left)}px`);
    anchor.setAttribute("aria-expanded", "true");
  }
  picker.hidden = false;
  renderPicker(store);
  input.focus();
}
