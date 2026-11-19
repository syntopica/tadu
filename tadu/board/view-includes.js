import { OPEN_COLUMNS } from "./open-columns.js";

// Whether a view shows a card before filters apply. A State rule that asks
// for states (from a summary chip, "View all N in list" or the Filter
// menu) widens All work to every state, which the rule then narrows.
export function viewIncludes(card, view, me, state) {
  switch (view) {
    case "mine":
      return me !== null && card.assignees.includes(me) && OPEN_COLUMNS.includes(card.column);
    case "all":
      return state?.op === "any" || OPEN_COLUMNS.includes(card.column);
    case "blocked":
      return card.column === "blocked";
    case "done":
      return card.column === "done";
    default:
      return true;
  }
}
