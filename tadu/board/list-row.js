import { avatar } from "./avatar.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { inlineTitle } from "./inline-title.js";
import { locationLabel } from "./location-label.js";
import { metaPart } from "./meta-part.js";
import { priorityBadge } from "./priority-badge.js";
import { statePill } from "./state-pill.js";

// One list item: a button that opens the detail panel. Desktop shows it as
// a compact row, a phone as a card; CSS places the same parts.
export function listRow(card, selected, me) {
  const row = el("button", `row state-${card.column}`);
  row.type = "button";
  row.dataset.key = card.key;
  row.classList.toggle("selected", selected);
  const place = card.project === null ? card.repository : `${card.project} / ${card.repository}`;
  const title = el("span", "row-title");
  title.title = card.title;
  title.append(inlineTitle(card.title));
  const facts = el("span", "row-facts");
  facts.append(metaPart("code", locationLabel(card), "row-location"));
  if (card.due !== null) {
    facts.append(metaPart("calendar", card.due, "row-due"));
  }
  for (const label of card.labels.slice(0, 2)) {
    facts.append(el("span", "label", label));
  }
  const side = el("span", "row-side");
  const priority = priorityBadge(card.priority);
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
    metaPart("branch", place, "row-place"),
    title,
    facts,
    side,
    who,
    icon("chevronRight", "icon row-chevron"),
  );
  return row;
}
