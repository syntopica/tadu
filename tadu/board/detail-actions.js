import { el } from "./el.js";
import { externalLink } from "./external-link.js";
import { safeEditor } from "./safe-editor.js";
import { safeRemote } from "./safe-remote.js";

// "Open in editor" and "View on remote", each only when its URL is safe.
export function detailActions(card) {
  const base = window.location.href;
  const actions = el("div", "detail-actions");
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
