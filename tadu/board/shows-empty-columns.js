// Whether the board draws its empty columns: when asked to, and whenever a
// card may be dropped on one (the page may change some repository's items).
export function showsEmptyColumns(store) {
  return store.showEmpty || (store.payload?.writable ?? []).length > 0;
}
