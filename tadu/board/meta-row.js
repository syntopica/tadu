import { el } from "./el.js";
import { locationLabel } from "./location-label.js";
import { metaPart } from "./meta-part.js";

// Where a card lives: project, repository and "TODO.md:61".
export function metaRow(card) {
  const row = el("span", "meta");
  if (card.project !== null) {
    row.append(metaPart("branch", card.project, "meta-project"));
  }
  row.append(metaPart("repo", card.repository, "meta-repo"));
  row.append(metaPart("file", locationLabel(card), "meta-file"));
  return row;
}
