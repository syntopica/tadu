import { whereParts } from "./where-parts.js";

// The chosen places named for a button or a title: "Acme Inc.", "Acme
// Inc., Globex CRM", or the first two and how many more ("A, B +2");
// `all` when none is chosen.
export function placesLabel(places, index, all) {
  if (places.length === 0) {
    return all;
  }
  const names = places.map((place) => whereParts(place, index).at(-1)?.label ?? "");
  const more = names.length > 2 ? ` +${names.length - 2}` : "";
  return `${names.slice(0, 2).join(", ")}${more}`;
}
