import { el } from "./el.js";
import { inPlaces } from "./in-places.js";
import { listRow } from "./list-row.js";

// The cards a tool call listed (its --json objects), in its order and inside
// the scope, under the title of their section when they have one (`urgent`
// groups by who acts). Objects whose card the board does not hold are left
// out. Returns the rows and the keys in order, for moving with J and K.
export function callCardRows(objects, store) {
  const rows = [];
  const keys = [];
  let section;
  for (const object of objects) {
    const card = store.byKey.get(object.key);
    if (card === undefined || !inPlaces(card, store.places)) {
      continue;
    }
    if (object.section !== undefined && object.section !== section) {
      section = object.section;
      rows.push(el("h2", "call-section", store.payload.sections?.[section] ?? section));
    }
    rows.push(listRow(card, store.selected === card.key, store.payload.me, { kind: true, priority: true }));
    keys.push(card.key);
  }
  return { rows, keys };
}
