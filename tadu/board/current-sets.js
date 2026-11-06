import { cardComparator } from "./card-comparator.js";
import { DEFAULT_FILTERS } from "./default-filters.js";
import { selectCards } from "./select-cards.js";

// The card sets one render needs: `board` (every state, for the summary
// chips), `view` (the current view before the state filter) and `shown`
// (what the page lists, sorted), and `total`, what it would list with no
// search, scope or filters.
export function currentSets(store) {
  const base = {
    filters: store.filters,
    scope: store.scope,
    me: store.payload?.me ?? null,
    text: store.text,
  };
  const board = selectCards(store.cards, store.texts, { ...base, view: "board" });
  const view =
    store.view === "board"
      ? board
      : selectCards(store.cards, store.texts, { ...base, view: store.view });
  const column = store.filters.column;
  const shown = (column === "" ? view : view.filter((card) => card.column === column)).sort(
    cardComparator(store.sort),
  );
  const plain = {
    ...base,
    filters: { ...DEFAULT_FILTERS, showCancelled: store.filters.showCancelled, column },
    scope: "all",
    text: "",
    view: store.view,
  };
  const total = selectCards(store.cards, store.texts, plain).filter(
    (card) => column === "" || card.column === column,
  ).length;
  return { board, view, shown, total };
}
