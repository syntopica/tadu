import { activeChips } from "./active-chips.js";
import { DEFAULT_FILTERS } from "./default-filters.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { requestRender } from "./request-render.js";

// The active filters as chips, each removable, and Clear for all of them.
export function renderChips(store) {
  const row = document.getElementById("active-chips");
  const chips = store.view === "portfolio" ? [] : activeChips(store.filters);
  row.hidden = chips.length === 0;
  row.replaceChildren(
    ...chips.map((chip) => {
      const node = el("span", "chip");
      const remove = el("button", "chip-remove");
      remove.type = "button";
      remove.setAttribute("aria-label", `Remove filter ${chip.label}`);
      remove.append(icon("close"));
      remove.addEventListener("click", () => {
        store.filters = { ...store.filters, [chip.name]: DEFAULT_FILTERS[chip.name] };
        requestRender();
      });
      node.append(el("span", "", chip.label), remove);
      return node;
    }),
  );
  if (chips.length > 0) {
    const clear = el("button", "link-button", "Clear");
    clear.type = "button";
    clear.addEventListener("click", () => {
      store.filters = { ...DEFAULT_FILTERS, project: store.filters.project };
      requestRender();
    });
    row.append(clear);
  }
}
