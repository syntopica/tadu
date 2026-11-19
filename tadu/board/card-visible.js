import { matchesRule } from "./matches-rule.js";
import { stateRule } from "./state-rule.js";

// Whether a card passes a filter choice: `choice` holds the filters (their
// rules but State, which the caller applies, waitingOnMe and
// showCancelled), me (or null) and today. A cancelled item shows only when
// cancelled items are shown or State asks for them; Waiting on me keeps
// what the server's `tadu inbox` of me lists.
export function cardVisible(card, choice) {
  const state = stateRule(choice);
  const asked = state?.op === "any" && state.values.includes("cancelled");
  if (card.column === "cancelled" && !choice.showCancelled && !asked) {
    return false;
  }
  for (const rule of choice.rules) {
    if (rule.field !== "state" && !matchesRule(card, rule, choice.today)) {
      return false;
    }
  }
  if (choice.waitingOnMe) {
    return choice.me !== null && card.waiting_on_me === true;
  }
  return true;
}
