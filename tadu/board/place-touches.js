import { placeCovers } from "./place-covers.js";

// Whether a row of the place `target` belongs in a tree narrowed to the
// chosen places: it holds one of them or lies inside one; every row does
// when none is chosen.
export function placeTouches(places, target, index) {
  return (
    places.length === 0 ||
    places.some((place) => placeCovers(place, target, index) || placeCovers(target, place, index))
  );
}
