import { cleanPlaces } from "./clean-places.js";
import { samePlaces } from "./same-places.js";

// A stored list of scopes (recent or starred) kept to the valid, distinct,
// non-empty ones the current workspace still has. Each scope is a list of
// places, or one place as scopes were stored before.
export function cleanPlacesList(raw, index) {
  const result = [];
  for (const entry of Array.isArray(raw) ? raw : []) {
    const places = cleanPlaces(entry, index);
    if (places.length > 0 && !result.some((old) => samePlaces(old, places))) {
      result.push(places);
    }
  }
  return result;
}
