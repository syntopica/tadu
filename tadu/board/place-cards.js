import { cardPlace } from "./card-place.js";

// The payload's cards, each with its `place` resolved once per load.
export function placeCards(cards, index) {
  return cards.map((card) => ({ ...card, place: cardPlace(card, index) }));
}
