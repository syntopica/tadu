import { activeChips } from "./active-chips.js";
import { DEFAULT_FILTERS } from "./default-filters.js";
import { el } from "./el.js";
import { EMPTY_WHERE } from "./empty-where.js";
import { icon } from "./icon.js";
import { requestRender } from "./request-render.js";
import { setWhere } from "./set-where.js";
import { whereParts } from "./where-parts.js";

// The chosen scope ("Company: Pixel Potion") and the active filters as
// chips, each removable: removing a scope level clears the levels below it.
// Clear empties the filters and keeps the scope.
export function renderChips(store) {
  const row = document.getElementById("active-chips");
  const chip = (label, kind, onRemove) => {
    const node = el("span", `chip ${kind}`);
    const remove = el("button", "chip-remove");
    remove.type = "button";
    remove.setAttribute("aria-label", `Remove ${label}`);
    remove.append(icon("close"));
    remove.addEventListener("click", onRemove);
    node.append(el("span", "", label), remove);
    return node;
  };
  const parts = store.index ? whereParts(store.where, store.index) : [];
  const levels = ["company", "project", "repository"];
  const scope = parts.map((part) =>
    chip(`${part.title}: ${part.label}`, "scope", () => {
      const kept = { ...EMPTY_WHERE };
      for (const level of levels.slice(0, levels.indexOf(part.level))) {
        kept[level] = store.where[level];
      }
      setWhere(kept);
    }),
  );
  const filters =
    store.view === "portfolio" || !store.index
      ? []
      : activeChips(store.filters, store.index.orgNames).map((found) =>
          chip(found.label, "filter", () => {
            store.filters = { ...store.filters, [found.name]: DEFAULT_FILTERS[found.name] };
            requestRender();
          }),
        );
  row.hidden = scope.length + filters.length === 0;
  row.replaceChildren(...scope, ...filters);
  if (filters.length > 0) {
    const clear = el("button", "link-button", "Clear filters");
    clear.type = "button";
    clear.addEventListener("click", () => {
      store.filters = { ...DEFAULT_FILTERS };
      requestRender();
    });
    row.append(clear);
  }
}
