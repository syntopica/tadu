import { OPEN_COLUMNS } from "./open-columns.js";

// Open items per repository key.
export function openCounts(cards) {
  const counts = new Map();
  for (const card of cards) {
    if (OPEN_COLUMNS.includes(card.column)) {
      counts.set(card.repository, (counts.get(card.repository) ?? 0) + 1);
    }
  }
  return counts;
}
