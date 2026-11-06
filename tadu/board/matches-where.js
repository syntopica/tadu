import { NO_PLACE } from "./no-place.js";

// Whether a card lies inside the chosen company, project and repository;
// "" chooses all and NO_PLACE the catch-all of cards without one.
export function matchesWhere(card, where) {
  if (where.repository !== "" && card.repository !== where.repository) {
    return false;
  }
  const project =
    where.project === NO_PLACE
      ? card.project === null
      : where.project === "" || card.project === where.project;
  if (!project) {
    return false;
  }
  if (where.company === NO_PLACE) {
    return card.place.companies.length === 0;
  }
  return where.company === "" || card.place.companies.includes(where.company);
}
