// The phone layout applies: lists instead of the kanban, a bottom nav.
export function isPhone() {
  return window.matchMedia("(max-width: 720px)").matches;
}
