import { el } from "./el.js";
import { locationLabel } from "./location-label.js";
import { metaPart } from "./meta-part.js";
import { placeLabel } from "./place-label.js";

// Where a card lives: "Company › Project" on a line of its own, then the
// repository when the column has room and "TODO.md:61-69" in full; the
// tooltip carries all of it.
export function metaRow(card) {
  const row = el("span", "meta");
  const location = locationLabel(card);
  const owner = placeLabel(card);
  row.title = `${owner === "" ? "" : `${owner} › `}${card.repository} · ${location}`;
  if (owner !== "") {
    row.append(metaPart("building", owner, "meta-place"));
  }
  row.append(metaPart("repo", card.repository, owner === "" ? "meta-only-repo" : "meta-repo"));
  row.append(metaPart("file", location, "meta-file"));
  return row;
}
