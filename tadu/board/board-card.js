import { cardBadges } from "./card-badges.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { inlineTitle } from "./inline-title.js";
import { metaRow } from "./meta-row.js";

// One kanban card; a button that opens the detail panel.
export function boardCard(card, selected) {
  const node = el("button", "card");
  node.type = "button";
  node.dataset.key = card.key;
  node.classList.toggle("selected", selected);
  const title = el("span", "card-title");
  title.title = card.title;
  title.append(inlineTitle(card.title));
  const head = el("span", "card-head");
  head.append(title);
  if (card.column === "done") {
    head.append(icon("done", "icon done-mark"));
  }
  node.append(head, metaRow(card));
  const badges = cardBadges(card);
  if (badges.childElementCount > 0) {
    node.append(badges);
  }
  return node;
}
