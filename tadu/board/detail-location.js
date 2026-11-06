import { copyButton } from "./copy-button.js";
import { el } from "./el.js";
import { locationLabel } from "./location-label.js";
import { metaPart } from "./meta-part.js";
import { shortId } from "./short-id.js";

// Project · repository · "TODO.md:275-288" with a copy button, and the ID.
export function detailLocation(card) {
  const where = el("div", "detail-location");
  if (card.project !== null) {
    where.append(metaPart("folder", card.project));
  }
  const location = locationLabel(card);
  const file = el("span", "nowrap");
  file.append(
    metaPart("file", location),
    copyButton(`${card.repository}:${location}`, "Copy location"),
  );
  where.append(metaPart("branch", card.repository), file);
  const id = el("div", "detail-id");
  const short = shortId(card);
  if (short === null) {
    id.append(el("span", "id-chip muted", "No ID (derived key, unstable)"));
  } else {
    const chip = el("span", "id-chip mono", short);
    chip.title = card.key;
    id.append(chip, copyButton(card.key, "Copy the full ID"));
  }
  return [where, id];
}
