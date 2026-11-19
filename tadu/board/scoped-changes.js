import { cardPlace } from "./card-place.js";
import { inPlaces } from "./in-places.js";

// The loaded changes (`payload`, as fetchChanges gives them) inside the
// chosen places, each with its place as a card has it.
export function scopedChanges(store, payload) {
  return (payload?.changes ?? [])
    .map((entry) => ({ ...entry, place: cardPlace(entry, store.index) }))
    .filter((entry) => inPlaces(entry, store.places));
}
