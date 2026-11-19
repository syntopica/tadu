import { samePlaces } from "./same-places.js";

// The recent scopes (each a list of places) with `places` first, without
// repeats, at most five; the whole workspace is not recorded.
export function pushRecent(recent, places) {
  if (places.length === 0) {
    return recent;
  }
  return [places, ...recent.filter((old) => !samePlaces(old, places))].slice(0, 5);
}
