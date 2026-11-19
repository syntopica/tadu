import { cardActions } from "./card-actions.js";

// The change a card dropped on a board column asks for: Backlog and Ready
// set the state open with the queue, In progress starts it, and Blocked,
// Done and Cancelled open the form that asks why. Null for its own column,
// or for a card that offers no change.
export function columnChange(card, column, me, tools) {
  const actions = Object.fromEntries(cardActions(card, me, tools).map((action) => [action.key, action.spec]));
  if (column === card.column || Object.keys(actions).length === 0) {
    return null;
  }
  const target = { id: card.key, repository: card.repository };
  const move = (title, args) => ({ title: `${title}: ${card.title}`, operation: "mark", args: { ...target, ...args }, fields: [] });
  switch (column) {
    case "backlog":
      return move("Back to the backlog", { state: "open", ...(card.queue === "ready" ? { queue: "backlog" } : {}) });
    case "ready":
      return move("Ready", { state: "open", queue: "ready" });
    case "in_progress":
      return move("In progress", { state: "in_progress" });
    case "blocked":
      return actions.block;
    case "done":
      return actions.done;
    case "cancelled":
      return actions.cancel;
    default:
      return null;
  }
}
