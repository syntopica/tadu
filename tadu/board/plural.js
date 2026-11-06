import { formatCount } from "./format-count.js";

// "1 warning", "2 warnings", "3 repositories": the count and the word,
// plural unless one.
export function plural(count, word) {
  const many = word.endsWith("y") ? `${word.slice(0, -1)}ies` : `${word}s`;
  return `${formatCount(count)} ${count === 1 ? word : many}`;
}
