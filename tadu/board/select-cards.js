import { cardVisible } from "./card-visible.js";
import { matchesQuery } from "./matches-query.js";
import { matchesScope } from "./matches-scope.js";
import { viewIncludes } from "./view-includes.js";

// Cards of the view that pass the filters, scope and search; the state
// filter (`filters.column`) is left to the caller so counts stay whole.
// `searchTexts` maps each card to its lowercased search text.
export function selectCards(cards, searchTexts, query) {
  const { view, filters, scope, me, text } = query;
  const choice = { ...filters, me };
  return cards.filter(
    (card) =>
      viewIncludes(card, view, me, filters.column) &&
      cardVisible(card, choice) &&
      (view !== "blocked" || matchesScope(card, scope, me)) &&
      (text === "" || matchesQuery(searchTexts.get(card), text)),
  );
}
