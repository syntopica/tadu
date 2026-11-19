import { boardCard } from "./board-card.js";
import { BOARD_COLUMN_CAP } from "./board-column-cap.js";
import { boardColumns } from "./board-columns.js";
import { columnCounts } from "./column-counts.js";
import { columnTitle } from "./column-title.js";
import { columnView } from "./column-view.js";
import { dragCard } from "./drag-card.js";
import { dropColumn } from "./drop-column.js";
import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { icon } from "./icon.js";
import { setView } from "./set-view.js";
import { shownBadges } from "./shown-badges.js";
import { showsEmptyColumns } from "./shows-empty-columns.js";
import { stateRule } from "./state-rule.js";

// The kanban: one column per shown state, each drawing at most
// BOARD_COLUMN_CAP cards and, when it holds more, linking to the full list.
// When the page may change a card, dragging it to another column changes
// its state.
export function renderBoard(store, sets, content) {
  const counts = columnCounts(sets.shown, store.payload.columns);
  let columns = boardColumns(
    store.payload.columns,
    counts,
    showsEmptyColumns(store),
    store.filters.showCancelled,
  );
  const state = stateRule(store.filters);
  if (state?.op === "any") {
    columns = store.payload.columns.filter((column) => state.values.includes(column));
  } else if (state !== null) {
    columns = columns.filter((column) => !state.values.includes(column));
  }
  const board = el("div", "board");
  const keys = [];
  const shown = shownBadges("state", store.filters);
  for (const column of columns) {
    const cards = sets.shown.filter((card) => card.column === column);
    const node = el("section", `column state-${column}`);
    node.setAttribute("aria-label", columnTitle(column, store.payload.done_days));
    const head = el("header", "column-head");
    head.append(
      el("h2", "", columnTitle(column, store.payload.done_days)),
      el("span", "count", formatCount(cards.length)),
    );
    const list = el("div", "column-cards");
    for (const card of cards.slice(0, BOARD_COLUMN_CAP)) {
      const node = boardCard(card, store.selected === card.key, shown);
      dragCard(node, card, store);
      list.append(node);
      keys.push(card.key);
    }
    if (cards.length === 0) {
      list.append(el("p", "empty", "Nothing here."));
    }
    dropColumn(node, column, store);
    node.append(head, list);
    if (cards.length > BOARD_COLUMN_CAP) {
      const more = el("button", "column-more");
      more.type = "button";
      more.append(
        el("span", "", `View all ${formatCount(cards.length)} in list`),
        icon("arrowRight"),
      );
      more.addEventListener("click", () => {
        const target = columnView(column);
        setView(target.view, target.column);
      });
      node.append(more);
    }
    board.append(node);
  }
  store.navKeys = keys;
  content.replaceChildren(board);
}
