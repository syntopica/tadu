import { closeDetail } from "./close-detail.js";
import { detailActions } from "./detail-actions.js";
import { detailFields } from "./detail-fields.js";
import { detailLocation } from "./detail-location.js";
import { detailMetadata } from "./detail-metadata.js";
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
  const description = el("section", "description");
  const label = el("h3");
  label.append(icon("text"), el("span", "", "Description (read only)"));
  description.append(label, el("pre", "mono", card.text));
  const body = el("div", "detail-body");
  body.append(title, ...detailLocation(card), detailFields(card), description);
  const warnings = detailWarnings(card);
  if (warnings) {
    body.append(warnings);
  }
  body.append(detailMetadata(card));
  panel.replaceChildren(head, body, detailActions(card));
  if (store.focusDetail) {
    store.focusDetail = false;
    close.focus({ preventScroll: true });
  }
}
