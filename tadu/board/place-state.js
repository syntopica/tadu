import { placeCovers } from "./place-covers.js";

// How a place reads in the scope tree for the chosen `places`: "checked"
// when one of them holds it (itself, or a company or project around it),
// "mixed" when it holds some of them, else "unchecked".
export function placeState(place, places, index) {
  if (places.some((chosen) => placeCovers(chosen, place, index))) {
    return "checked";
  }
  return places.some((chosen) => placeCovers(place, chosen, index)) ? "mixed" : "unchecked";
}
