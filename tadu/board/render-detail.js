import { closeDetail } from "./close-detail.js";
import { detailActions } from "./detail-actions.js";
import { detailDescription } from "./detail-description.js";
import { detailFields } from "./detail-fields.js";
import { detailFile } from "./detail-file.js";
import { detailHistory } from "./detail-history.js";
import { detailLocation } from "./detail-location.js";
import { detailMetadata } from "./detail-metadata.js";
import { detailRelations } from "./detail-relations.js";
import { detailTaskFields } from "./detail-task-fields.js";
import { detailWarnings } from "./detail-warnings.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { inlineTitle } from "./inline-title.js";

// The side panel (a full-screen sheet on a phone) of the selected item.
export function renderDetail(store) {
  const panel = document.getElementById("detail");
  const card = store.detail ? store.byKey.get(store.selected) : undefined;
  document.body.classList.toggle("detail-open", card !== undefined);
  panel.hidden = card === undefined;
  if (card === undefined) {
    panel.shownCard = undefined;
    panel.replaceChildren();
    return;
  }
  if (panel.shownCard === card && !store.focusDetail) {
    return;
  }
  // A reload rebuilds the panel; on the same item the History section keeps its
  // filter, and stays open if it was.
  const history = panel.querySelector("details.history");
  const sameItem = panel.shownCard?.key === card.key;
  const keepHistory = sameItem && history?.open === true;
  const historyFilter = sameItem ? history?.historyFilter : undefined;
  panel.shownCard = card;
  const head = el("header", "detail-head");
  const close = el("button", "icon-button");
  close.type = "button";
  close.setAttribute("aria-label", "Close the detail (Esc)");
  close.title = "Close (Esc)";
  close.append(icon("close"));
  close.addEventListener("click", closeDetail);
  head.append(icon("text"), el("span", "", "Item detail"), close);
  const title = el("h2", "detail-title");
  title.title = card.title;
  title.append(inlineTitle(card.title));
  const body = el("div", "detail-body");
  body.append(title, ...detailLocation(card), detailFields(card));
  // Each part below is left out when the item has none of it.
  const parts = [
    detailTaskFields(card),
    detailDescription(card),
    detailRelations(card, store.byKey),
    detailWarnings(card),
    detailMetadata(card),
    card.path.endsWith(".json") ? detailFile(card) : null,
  ];
  body.append(...parts.filter((part) => part !== null));
  body.append(detailHistory(card, keepHistory, historyFilter));
  // A rebuild (a reload, or a change made from here) keeps the focus in the
  // panel: on the same action button when there is one, else on Close.
  const focused = document.activeElement;
  const hadFocus = focused?.closest?.("#detail") === panel;
  const actions = detailActions(card, store);
  panel.replaceChildren(head, body, actions);
  const again = hadFocus && focused.dataset?.action
    ? actions.querySelector(`[data-action="${focused.dataset.action}"]`)
    : null;
  if (store.focusDetail || hadFocus) {
    store.focusDetail = false;
    (again ?? close).focus({ preventScroll: true });
  }
}
