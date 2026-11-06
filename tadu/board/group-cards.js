import { groupValue } from "./group-value.js";

// Cards split into ordered groups, keeping the card order inside each group.
export function groupCards(cards, group) {
  const groups = new Map();
  for (const card of cards) {
    const value = groupValue(card, group);
    if (!groups.has(value.key)) {
      groups.set(value.key, { ...value, cards: [] });
    }
    groups.get(value.key).cards.push(card);
  }
  return [...groups.values()].sort((a, b) => (a.order < b.order ? -1 : a.order > b.order ? 1 : 0));
}
