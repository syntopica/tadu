import { canChange } from "./can-change.js";
import { OPEN_COLUMNS } from "./open-columns.js";

// Let an open card the page may change be dragged to another column;
// `store.dragging` holds its key while it is. A screen reader hears that it
// can be dragged, and that its detail makes the same changes.
export function dragCard(node, card, store) {
  if (!OPEN_COLUMNS.includes(card.column) || !canChange(store.payload, card.repository)) {
    return;
  }
  node.draggable = true;
  node.setAttribute("aria-describedby", "drag-hint");
  node.addEventListener("dragstart", (event) => {
    store.dragging = card.key;
    event.dataTransfer?.setData("text/plain", card.key);
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = "move";
    }
  });
  node.addEventListener("dragend", () => {
    store.dragging = null;
  });
}
