// Portfolio rows: catch-all rows last, then by total, largest first, then by name.
export function compareRows(a, b) {
  if (a.last !== b.last) {
    return a.last ? 1 : -1;
  }
  return b.buckets.total - a.buckets.total || (a.label < b.label ? -1 : a.label > b.label ? 1 : 0);
}
