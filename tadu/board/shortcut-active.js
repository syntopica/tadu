// Whether All work shows exactly what a sidebar shortcut opens: the same
// rules and Waiting on me.
export function shortcutActive(shortcut, view, filters) {
  const rules = shortcut.filters.rules ?? [];
  const waiting = shortcut.filters.waitingOnMe === true;
  return view === "all" && JSON.stringify(filters.rules) === JSON.stringify(rules) && filters.waitingOnMe === waiting;
}
