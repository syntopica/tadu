import { DEFAULT_FILTERS } from "./default-filters.js";
import { el } from "./el.js";
import { filterChip } from "./filter-chip.js";
import { ITEM_FIELDS } from "./item-fields.js";
import { itemFilterSource } from "./item-filter-source.js";
import { openFilterMenu } from "./open-filter-menu.js";
import { ownView } from "./own-view.js";
import { requestRender } from "./request-render.js";
import { ruleParts } from "./rule-parts.js";
import { valueLabel } from "./value-label.js";

// The active filters as chips under the toolbar, in the order they were
// added: a click on one edits it in the Filter menu, its cross removes it.
// Clear all and Save view follow; the row hides when no filter is on.
export function renderChips(store) {
  const row = document.getElementById("active-chips");
  const shown = store.view !== "portfolio" && !ownView(store.view) && store.index !== null;
  const filters = store.filters;
  if (!shown || (filters.rules.length === 0 && !filters.waitingOnMe)) {
    row.hidden = true;
    row.replaceChildren();
    return;
  }
  const me = store.payload.me ?? null;
  const change = (next) => {
    store.filters = { ...store.filters, ...next };
    requestRender();
  };
  const chips = filters.rules.map((rule) => {
    const field = ITEM_FIELDS.find((entry) => entry.key === rule.field);
    const label = (value) => valueLabel(rule.field, value, store.index.orgNames, me);
    return filterChip(
      ruleParts(rule, field.title, label),
      (anchor) => openFilterMenu(itemFilterSource(store), anchor, rule.field),
      () => change({ rules: store.filters.rules.filter((old) => old !== rule) }),
    );
  });
  if (filters.waitingOnMe) {
    const chip = filterChip(
      { title: "Waiting on me", op: "", values: "" },
      (anchor) => openFilterMenu(itemFilterSource(store), anchor),
      () => change({ waitingOnMe: false }),
    );
    chip.classList.add("quick");
    chips.push(chip);
  }
  const clear = el("button", "link-button", "Clear all");
  clear.type = "button";
  clear.addEventListener("click", () =>
    change({ ...DEFAULT_FILTERS, showCancelled: store.filters.showCancelled }),
  );
  const save = el("button", "link-button muted-link", "Save view");
  save.type = "button";
  save.addEventListener("click", () => {
    store.navOpen = true;
    requestRender();
    window.requestAnimationFrame(() => document.getElementById("save-view-name").focus());
  });
  row.hidden = false;
  row.replaceChildren(...chips, clear, save);
}
