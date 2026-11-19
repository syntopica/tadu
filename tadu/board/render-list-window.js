import { el } from "./el.js";
import { groupRow } from "./group-row.js";
import { listRow } from "./list-row.js";
import { requestRender } from "./request-render.js";
import { shownBadges } from "./shown-badges.js";
import { visibleWindow } from "./visible-window.js";

// Draw only the rows that cover the viewport, absolutely positioned inside
// a spacer as tall as the whole list.
export function renderListWindow(store, list) {
  const { rows, offsets, spacer } = list;
  const top = -spacer.getBoundingClientRect().top;
  const { start, end } = visibleWindow(offsets, top, window.innerHeight, 8);
  if (list.start === start && list.end === end && !list.dirty) {
    return;
  }
  list.start = start;
  list.end = end;
  list.dirty = false;
  const me = store.payload?.me ?? null;
  const shown = shownBadges(store.group, store.filters);
  const nodes = [];
  for (let index = start; index < end; index += 1) {
    const row = rows[index];
    const node =
      row.kind === "group"
        ? groupRow(row, (key) => {
            if (store.collapsed.has(key)) {
              store.collapsed.delete(key);
            } else {
              store.collapsed.add(key);
            }
            requestRender();
          })
        : listRow(row.card, store.selected === row.card.key, me, shown);
    const item = el("div", "virtual");
    item.setAttribute("role", "listitem");
    item.setAttribute("aria-posinset", String(index + 1));
    item.setAttribute("aria-setsize", String(rows.length));
    item.style.setProperty("--row-top", `${offsets[index]}px`);
    item.style.setProperty("--row-height", `${offsets[index + 1] - offsets[index]}px`);
    item.append(node);
    nodes.push(item);
  }
  const focused = document.activeElement?.dataset?.key;
  spacer.replaceChildren(...nodes);
  if (focused) {
    spacer.querySelector(`[data-key="${CSS.escape(focused)}"]`)?.focus({ preventScroll: true });
  }
}
