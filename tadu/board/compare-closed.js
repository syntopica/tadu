import { compareText } from "./compare-text.js";

// Most recently closed first; cards without a closing day last.
export function compareClosed(a, b) {
  return compareText(b.day ?? "", a.day ?? "");
}
