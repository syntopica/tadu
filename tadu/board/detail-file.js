import { el } from "./el.js";
import { foldedSummary } from "./folded-summary.js";

// A task's file as it is on disk, folded: the panel draws its fields, and
// this keeps whatever else it holds (team `x-` keys) in view.
export function detailFile(card) {
  const details = el("details", "metadata task-source");
  details.append(foldedSummary("code", "Task file"), el("pre", "mono", card.text));
  return details;
}
