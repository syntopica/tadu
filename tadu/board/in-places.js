import { matchesWhere } from "./matches-where.js";

// Whether a card (or a change, which carries the same place) lies in any of
// the chosen places; no place chosen is the whole workspace.
export function inPlaces(card, places) {
  return places.length === 0 || places.some((place) => matchesWhere(card, place));
}
