import { cardVisible } from "./card-visible.js";
import { inPlaces } from "./in-places.js";
import { matchesQuery } from "./matches-query.js";
import { matchesScope } from "./matches-scope.js";
import { stateRule } from "./state-rule.js";
import { viewIncludes } from "./view-includes.js";

// Cards of the view inside the chosen places (`places`, none for the
// whole workspace) that pass the filters, Blocked sub-chip and search; the State
// rule is left to the caller so counts stay whole. `searchTexts` maps each
// card to its lowercased search text.
export function selectCards(cards, searchTexts, query) {
  const { view, filters, scope, places, me, text } = query;
  const choice = { ...filters, me, today: query.today ?? "" };
  const state = stateRule(filters);
  return cards.filter(
    (card) =>
      inPlaces(card, places) &&
      viewIncludes(card, view, me, state) &&
      cardVisible(card, choice) &&
      (view !== "blocked" || matchesScope(card, scope, me)) &&
      (text === "" || matchesQuery(searchTexts.get(card), text)),
  );
}
