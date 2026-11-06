import { el } from "./el.js";
import { locationLabel } from "./location-label.js";
import { metaPart } from "./meta-part.js";

// Where a card lives: one place name (the project, else the repository),
// the repository too when the column has room, and "TODO.md:61-69" in full.
export function metaRow(card) {
  const row = el("span", "meta");
  const location = locationLabel(card);
  const where = card.project === null ? card.repository : `${card.project} / ${card.repository}`;
  row.title = `${where} · ${location}`;
  if (card.project === null) {
    row.append(metaPart("repo", card.repository, "meta-place"));
  } else {
    row.append(metaPart("branch", card.project, "meta-place"));
    row.append(metaPart("repo", card.repository, "meta-repo"));
  }
  row.append(metaPart("file", location, "meta-file"));
  return row;
}
