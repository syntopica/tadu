import { samePlaces } from "./same-places.js";

// The starred scopes (each a list of places) with `places` added, or
// removed when already starred.
export function toggleFavourite(favourites, places) {
  if (favourites.some((old) => samePlaces(old, places))) {
    return favourites.filter((old) => !samePlaces(old, places));
  }
  return [...favourites, places];
}
