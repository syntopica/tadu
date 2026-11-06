import { el } from "./el.js";
import { groupCards } from "./group-cards.js";
import { isPhone } from "./is-phone.js";
import { LIST_HEIGHTS } from "./list-heights.js";
import { listEmptyText } from "./list-empty-text.js";
import { listRows } from "./list-rows.js";
import { meMissing } from "./me-missing.js";
import { renderListWindow } from "./render-list-window.js";
import { rowOffsets } from "./row-offsets.js";

// The grouped, virtualized list of a view.
export function renderList(store, sets, content) {
  store.list = null;
  if (store.view === "mine" && !store.payload.me) {
    store.navKeys = [];
    content.replaceChildren(meMissing());
    return;
  }
  if (sets.shown.length === 0) {
    store.navKeys = [];
    const filtered = sets.shown.length !== sets.view.length || store.text !== "";
    content.replaceChildren(el("p", "empty-state", listEmptyText(store.view, filtered)));
    return;
  }
  const rows = listRows(groupCards(sets.shown, store.group), store.collapsed);
  const heights = isPhone() ? LIST_HEIGHTS.phone : LIST_HEIGHTS.desktop;
  const offsets = rowOffsets(rows, heights.group, heights.card);
  const spacer = el("div", "vlist");
  spacer.setAttribute("role", "list");
  spacer.style.setProperty("--list-height", `${offsets[offsets.length - 1]}px`);
  content.replaceChildren(spacer);
  store.navKeys = rows.filter((row) => row.kind === "card").map((row) => row.card.key);
  store.list = { rows, offsets, spacer, start: -1, end: -1, dirty: true };
  renderListWindow(store, store.list);
}
