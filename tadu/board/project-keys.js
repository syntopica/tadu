// Project keys of the workspace, busiest first.
export function projectKeys(cards) {
  const counts = new Map();
  for (const card of cards) {
    if (card.project !== null) {
      counts.set(card.project, (counts.get(card.project) ?? 0) + 1);
    }
  }
  return [...counts.keys()].sort((a, b) => counts.get(b) - counts.get(a) || (a < b ? -1 : 1));
}
