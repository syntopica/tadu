import { compareText } from "./compare-text.js";

// Alphabetical by title, ignoring case.
export function compareTitle(a, b) {
  return compareText(a.title.toLowerCase(), b.title.toLowerCase());
}
