import { cleanWhere } from "./clean-where.js";
import { placeCovers } from "./place-covers.js";
import { placeKey } from "./place-key.js";

// Chosen places from a URL, storage or a saved view made valid for the
// current workspace: each cleaned as cleanWhere does (one place alone, as
// scopes were stored before several could be chosen, counts as a list of
// one), unknown ones dropped, repeats and places inside another chosen one
// left out. A blank place is the whole workspace: the list is then empty.
export function cleanPlaces(raw, index) {
  const given = Array.isArray(raw) ? raw : raw !== null && typeof raw === "object" ? [raw] : [];
  const text = (value) => (typeof value === "string" ? value : "");
  const blank = (entry) => ["company", "project", "repository"].every((level) => text(entry?.[level]) === "");
  if (given.some(blank)) {
    return [];
  }
  const places = [];
  for (const place of given.map((entry) => cleanWhere(entry, index))) {
    const key = placeKey(place);
    if (key !== "" && !places.some((old) => placeKey(old) === key)) {
      places.push(place);
    }
  }
  return places.filter((place) => !places.some((other) => other !== place && placeCovers(other, place, index)));
}
