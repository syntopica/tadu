import { compareText } from "./compare-text.js";

// Order by repository, then path, then line.
export function compareLocation(a, b) {
  return compareText(a.repository, b.repository) || compareText(a.path, b.path) || a.line - b.line;
}
