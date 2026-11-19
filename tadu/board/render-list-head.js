import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { isPhone } from "./is-phone.js";
import { ownView } from "./own-view.js";
import { requestRender } from "./request-render.js";
import { scopeChip } from "./scope-chip.js";

// Above a list: its heading and count, and the Blocked view's scope chips.
export function renderListHead(store, sets) {
  const head = document.getElementById("list-head");
  const list = store.view !== "portfolio" && !ownView(store.view) && (store.view !== "board" || isPhone());
  head.hidden = !list || !store.payload;
  if (head.hidden) {
    return;
  }
  const title =
    { blocked: "All blocked", mine: "Assigned to me", done: "Recently closed" }[store.view] ??
    "Items";
  const top = el("div", "list-head-row");
  const heading = el("h2", "", title);
  heading.append(el("span", "count", formatCount(sets.shown.length)));
  top.append(heading);
  head.replaceChildren(top);
  if (store.view === "blocked") {
    const me = store.payload.me;
    const chips = el("div", "scope-chips");
    for (const [scope, label] of [
      ["all", "All"],
      ["mine", "Blocked for me"],
      ["unassigned", "Unassigned"],
    ]) {
      if (scope === "mine" && !me) {
        continue;
      }
      chips.append(
        scopeChip(label, store.scope === scope, () => {
          store.scope = scope;
          requestRender();
        }),
      );
    }
    head.append(chips);
  }
}
