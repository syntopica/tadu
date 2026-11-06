import { formatCount } from "./format-count.js";

// "1 warning", "2 warnings": the count and the word, plural unless one.
export function plural(count, word) {
  return `${formatCount(count)} ${count === 1 ? word : `${word}s`}`;
}
