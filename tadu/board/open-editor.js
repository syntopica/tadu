import { safeEditor } from "./safe-editor.js";

// Follow the selected card's editor link, when it has a safe one.
export function openEditor(card) {
  if (!card || !safeEditor(card.editor_url, window.location.href)) {
    return;
  }
  window.open(card.editor_url, "_blank", "noopener,noreferrer");
}
