// Index of the last row whose top is at or above `top` (binary search).
export function firstRowBelow(offsets, top) {
  let low = 0;
  let high = offsets.length - 2;
  while (low < high) {
    const middle = Math.ceil((low + high) / 2);
    if (offsets[middle] <= top) {
      low = middle;
    } else {
      high = middle - 1;
    }
  }
  return Math.max(low, 0);
}
