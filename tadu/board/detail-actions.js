import { canChange } from "./can-change.js";
import { cardActions } from "./card-actions.js";
import { el } from "./el.js";
import { externalLink } from "./external-link.js";
import { openChange } from "./open-change.js";
import { safeEditor } from "./safe-editor.js";
import { safeRemote } from "./safe-remote.js";

// The changes the page may make to the item (when the board and the
// repository allow them), then "Open in editor" and "View on remote", each
// only when its URL is safe.
export function detailActions(card, store) {
  const base = window.location.href;
  const actions = el("div", "detail-actions");
  if (canChange(store.payload, card.repository)) {
    const changes = el("div", "change-actions");
    for (const action of cardActions(card, store.payload.me, store.payload.tools)) {
      const button = el("button", "button", action.label);
      button.type = "button";
      button.dataset.action = action.key;
      button.addEventListener("click", () => openChange(store, action.spec, button));
      changes.append(button);
    }
    if (changes.childElementCount > 0) {
      actions.append(changes);
    }
  }
  if (safeEditor(card.editor_url, base)) {
    actions.append(externalLink("Open in editor", card.editor_url, "button primary"));
  }
  if (safeRemote(card.remote_url, base)) {
    actions.append(externalLink("View on remote", card.remote_url, "button"));
  }
  if (actions.childElementCount === 0) {
    actions.append(el("p", "muted", "No editor or remote link is configured for this repository."));
  }
  return actions;
}
