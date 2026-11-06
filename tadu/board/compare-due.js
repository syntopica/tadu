import { compareText } from "./compare-text.js";

// Earliest due date first; cards without one last.
export function compareDue(a, b) {
  if (a.due === b.due) {
    return 0;
  }
  if (a.due === null) {
    return 1;
  }
  if (b.due === null) {
    return -1;
  }
  return compareText(a.due, b.due);
}
