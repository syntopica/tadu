import { cardVisible } from "./card-visible.js";
import { matchesQuery } from "./matches-query.js";
import { matchesScope } from "./matches-scope.js";
import { matchesWhere } from "./matches-where.js";
import { viewIncludes } from "./view-includes.js";

// Cards of the view inside the chosen company, project and repository
// (`where`) that pass the filters, Blocked sub-chip and search; the state
// filter (`filters.column`) is left to the caller so counts stay whole.
// `searchTexts` maps each card to its lowercased search text.
export function selectCards(cards, searchTexts, query) {
  const { view, filters, scope, where, me, text } = query;
  const choice = { ...filters, me };
  return cards.filter(
    (card) =>
      matchesWhere(card, where) &&
      viewIncludes(card, view, me, filters.column) &&
      cardVisible(card, choice) &&
      (view !== "blocked" || matchesScope(card, scope, me)) &&
      (text === "" || matchesQuery(searchTexts.get(card), text)),
  );
}
