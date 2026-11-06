import { FILTER_VALUES } from "./filter-values.js";
import { matchesOrganization } from "./matches-organization.js";
import { SINGLE_FILTERS } from "./single-filters.js";

// `choice` holds each filter's selected value ("" for any), the toggles
// unassigned, noPriority, waitingOnMe and showCancelled, and me (or null).
export function cardVisible(card, choice) {
  if (card.column === "cancelled" && !choice.showCancelled) {
    return false;
  }
  for (const name of SINGLE_FILTERS) {
    if (choice[name] !== "" && !FILTER_VALUES[name](card).includes(choice[name])) {
      return false;
    }
  }
  if (!matchesOrganization(card, choice.organization, choice.role)) {
    return false;
  }
  if (choice.unassigned && card.assignees.length > 0) {
    return false;
  }
  if (choice.noPriority && card.priority !== null) {
    return false;
  }
  if (choice.waitingOnMe) {
    return card.column === "blocked" && choice.me !== null && card.assignees.includes(choice.me);
  }
  return true;
}
