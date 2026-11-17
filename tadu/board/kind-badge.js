import { el } from "./el.js";
import { KIND_TITLES } from "./kind-titles.js";

// "Decision", "Waiting on others" or "Later"; null for a task and for an
// unclassified item, so ordinary work stays unmarked.
export function kindBadge(kind) {
  if (kind === "task" || !(kind in KIND_TITLES)) {
    return null;
  }
  return el("span", `badge kind kind-${kind}`, KIND_TITLES[kind]);
}
