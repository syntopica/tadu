// Whether All work shows exactly what a sidebar shortcut opens.
export function shortcutActive(shortcut, view, filters) {
  const wanted = { kind: "", waitingOnMe: false, ...shortcut.filters };
  return view === "all" && filters.kind === wanted.kind && filters.waitingOnMe === wanted.waitingOnMe;
}
