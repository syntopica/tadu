// Scope entries busiest first: most open items, then by name.
export function compareOpen(a, b) {
  return b.open - a.open || (a.name < b.name ? -1 : a.name > b.name ? 1 : 0);
}
