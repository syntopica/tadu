import { avatar } from "./avatar.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { inlineTitle } from "./inline-title.js";
import { kindBadge } from "./kind-badge.js";
import { locationLabel } from "./location-label.js";
import { metaPart } from "./meta-part.js";
import { placeLabel } from "./place-label.js";
import { priorityBadge } from "./priority-badge.js";
import { statePill } from "./state-pill.js";

// One list item: a button that opens the detail panel. Desktop shows it as
// a compact row, a phone as a card; CSS places the same parts. A kind other
// than task leads the title, where a scan of the list meets it first,
// unless `shown` says the list already says it, as for the priority.
export function listRow(card, selected, me, shown) {
  const row = el("button", `row state-${card.column}`);
  row.type = "button";
  row.dataset.key = card.key;
  row.classList.toggle("selected", selected);
  const owner = placeLabel(card);
  const place = owner === "" ? card.repository : `${owner} › ${card.repository}`;
  const title = el("span", "row-title");
  title.title = card.title;
  const kind = shown.kind ? kindBadge(card.kind) : null;
  title.append(...(kind ? [kind] : []), inlineTitle(card.title));
  const facts = el("span", "row-facts");
  facts.append(metaPart("code", locationLabel(card), "row-location"));
  if (card.due !== null) {
    facts.append(metaPart("calendar", card.due, "row-due"));
  }
  if (card.check_on !== null) {
    facts.append(metaPart("clock", `Check ${card.check_on}`, "row-due row-check"));
  }
  for (const label of card.labels.slice(0, 2)) {
    facts.append(el("span", "label", label));
  }
  const side = el("span", "row-side");
  const priority = shown.priority ? priorityBadge(card.priority) : null;
  side.append(...(priority ? [priority] : []), statePill(card.column));
  const who = el("span", "row-who");
  if (card.assignees.length === 0) {
    who.append(el("span", "muted-pill", "Unassigned"));
  } else {
    const mine = me !== null && card.assignees.includes(me);
    who.append(avatar(card.assignees[0]), el("span", "who-name", mine ? "Me" : card.assignees[0]));
  }
  row.append(
    el("span", "row-rule"),
    metaPart(owner === "" ? "repo" : "building", place, "row-place"),
    title,
    facts,
    side,
    who,
    icon("chevronRight", "icon row-chevron"),
  );
  return row;
}
