import { cardComparator } from "./card-comparator.js";
import { DEFAULT_FILTERS } from "./default-filters.js";
import { matchesRule } from "./matches-rule.js";
import { portfolioCards } from "./portfolio-cards.js";
import { selectCards } from "./select-cards.js";
import { stateRule } from "./state-rule.js";

// The card sets one render needs, all inside the chosen places
// (`store.places`): `board` (every state, for the summary chips), `view`
// (the current view before the State rule), `shown` (what the page lists,
// sorted), `base` (the searched view with no filter, every state of All
// work included: what the Filter menu counts) and `total`, what the page
// would list with no search or filter but State. In the portfolio, `shown`
// and `total` are the cards its stat cards count, with and without its
// state filter.
export function currentSets(store) {
  const today = store.payload?.today ?? "";
  const base = {
    filters: store.filters,
    scope: store.scope,
    places: store.places,
    me: store.payload?.me ?? null,
    today,
    text: store.text,
  };
  const board = selectCards(store.cards, store.texts, { ...base, view: "board" });
  const view =
    store.view === "board"
      ? board
      : selectCards(store.cards, store.texts, { ...base, view: store.view });
  const state = stateRule(store.filters);
  const inState = (card) => state === null || matchesRule(card, state, today);
  const shown = view.filter(inState).sort(cardComparator(store.sort));
  const plain = {
    ...base,
    filters: { ...DEFAULT_FILTERS, showCancelled: store.filters.showCancelled, rules: state ? [state] : [] },
    scope: "all",
    text: "",
    view: store.view,
  };
  const total = selectCards(store.cards, store.texts, plain).filter(inState).length;
  const counted = {
    ...plain,
    filters: { ...plain.filters, rules: [] },
    text: store.text,
    view: store.view === "all" ? "board" : store.view,
  };
  const searched = selectCards(store.cards, store.texts, counted);
  if (store.view === "portfolio") {
    const stated = portfolioCards(store.cards, store.portfolio.state, store.places);
    const all = portfolioCards(store.cards, "", store.places);
    return { board, view, shown: stated, base: all, total: all.length };
  }
  return { board, view, shown, base: searched, total };
}
