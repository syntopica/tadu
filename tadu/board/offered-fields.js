import { distinctValues } from "./distinct-values.js";
import { ITEM_FIELDS } from "./item-fields.js";

// The item fields worth filtering by in these cards: state, assignee,
// priority and due date always; kind when some item has one (TODO.md);
// the others when some card holds a value.
export function offeredFields(cards) {
  return ITEM_FIELDS.filter((field) => {
    if (["state", "assignee", "priority", "due"].includes(field.key)) {
      return true;
    }
    if (field.key === "kind") {
      return cards.some((card) => card.kind !== null);
    }
    return distinctValues(cards, field.key).length > 0;
  });
}
