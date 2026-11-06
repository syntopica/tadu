// How many cards each column holds, every column present.
export function columnCounts(cards, columns) {
  const counts = Object.fromEntries(columns.map((column) => [column, 0]));
  for (const card of cards) {
    counts[card.column] = (counts[card.column] ?? 0) + 1;
  }
  return counts;
}
