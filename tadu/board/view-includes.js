import { OPEN_COLUMNS } from "./open-columns.js";

// Whether a view shows a card before filters apply. A state chosen from a
// board column ("View all N in list") widens All work to that state.
export function viewIncludes(card, view, me, column) {
  switch (view) {
    case "mine":
      return me !== null && card.assignees.includes(me) && OPEN_COLUMNS.includes(card.column);
    case "all":
      return column !== "" || OPEN_COLUMNS.includes(card.column);
    case "blocked":
      return card.column === "blocked";
    case "done":
      return card.column === "done";
    default:
      return true;
  }
}
