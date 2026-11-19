import { placeChildren } from "./place-children.js";
import { placeCovers } from "./place-covers.js";
import { placeKey } from "./place-key.js";
import { placeState } from "./place-state.js";

// The chosen places after ticking or unticking `place` in the scope tree.
// Ticking it replaces whatever it holds. Unticking a place chosen through
// a company or project around it splits that one into its other parts, so
// everything else it held stays chosen.
export function togglePlace(places, place, index) {
  const key = placeKey(place);
  if (placeState(place, places, index) !== "checked") {
    return [...places.filter((chosen) => !placeCovers(place, chosen, index)), place];
  }
  const result = [];
  const split = (outer) => {
    for (const child of placeChildren(outer, index)) {
      if (placeKey(child) === key) {
        continue;
      }
      if (placeCovers(child, place, index)) {
        split(child);
      } else {
        result.push(child);
      }
    }
  };
  for (const chosen of places) {
    if (placeKey(chosen) === key) {
      continue;
    }
    if (placeCovers(chosen, place, index)) {
      split(chosen);
    } else {
      result.push(chosen);
    }
  }
  return result;
}
