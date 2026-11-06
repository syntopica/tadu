import { firstRowBelow } from "./first-row-below.js";

// Rows [start, end) that cover the viewport [top, top + height), widened by
// `overscan` rows on each side.
export function visibleWindow(offsets, top, height, overscan) {
  const count = offsets.length - 1;
  if (count <= 0) {
    return { start: 0, end: 0 };
  }
  const first = firstRowBelow(offsets, Math.max(top, 0));
  let last = first;
  while (last < count && offsets[last] < top + height) {
    last += 1;
  }
  return { start: Math.max(first - overscan, 0), end: Math.min(last + overscan, count) };
}
