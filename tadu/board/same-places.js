import { placeKey } from "./place-key.js";

// Whether two lists of chosen places choose the same places, in any order.
export function samePlaces(a, b) {
  const keys = (places) => places.map(placeKey).sort().join("\n");
  return a.length === b.length && keys(a) === keys(b);
}
