import { columnChange } from "./column-change.js";
import { openChange } from "./open-change.js";

// Make a board column take the dragged card: it lights up while a card
// that may move there is over it, and a drop makes the change the column
// asks for (see columnChange).
export function dropColumn(node, column, store) {
  const change = () => {
    const card = store.byKey.get(store.dragging);
    return card ? columnChange(card, column, store.payload.me, store.payload.tools) : null;
  };
  node.addEventListener("dragover", (event) => {
    if (change() !== null) {
      event.preventDefault();
      node.classList.add("drop-target");
    }
  });
  node.addEventListener("dragleave", () => node.classList.remove("drop-target"));
  node.addEventListener("drop", (event) => {
    event.preventDefault();
    node.classList.remove("drop-target");
    const spec = change();
    store.dragging = null;
    if (spec !== null) {
      openChange(store, spec);
    }
  });
}
