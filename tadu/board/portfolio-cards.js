import { inPlaces } from "./in-places.js";

// The cards the portfolio counts: not cancelled, in the state filter (Ready
// counts as Backlog) and inside the scope.
export function portfolioCards(cards, state, places) {
  return cards.filter(
    (card) =>
      card.column !== "cancelled" &&
      (state === "" || card.column === state || (state === "backlog" && card.column === "ready")) &&
      inPlaces(card, places),
  );
}
