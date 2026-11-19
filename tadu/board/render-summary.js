import { columnCounts } from "./column-counts.js";
import { columnTitle } from "./column-title.js";
import { columnView } from "./column-view.js";
import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { isPhone } from "./is-phone.js";
import { ownView } from "./own-view.js";
import { requestRender } from "./request-render.js";
import { setView } from "./set-view.js";
import { showsEmptyColumns } from "./shows-empty-columns.js";
import { stateRule } from "./state-rule.js";
import { summaryOrder } from "./summary-order.js";

// One chip per state with its real count under the active filters; the
// empty Ready column says it is hidden.
export function renderSummary(store, sets) {
  const row = document.getElementById("summary");
  row.hidden = store.view === "portfolio" || ownView(store.view) || !store.payload;
  if (row.hidden) {
    return;
  }
  const columns = store.payload.columns;
  const counts = columnCounts(sets.board, columns);
  const phone = isPhone();
  const shown = summaryOrder(
    columns.filter((column) => column !== "cancelled" || store.filters.showCancelled),
    phone,
  );
  const state = stateRule(store.filters);
  const only = state?.op === "any" && state.values.length === 1 ? state.values[0] : "";
  row.replaceChildren(
    ...shown.map((column) => {
      const chip = el("button", `summary-chip state-${column}`);
      chip.type = "button";
      const target = columnView(column);
      const active =
        store.view === target.view && (target.column === "" || only === column);
      chip.classList.toggle("active", active && store.view !== "board");
      chip.classList.toggle("phone-hidden", phone && counts[column] === 0 && !active);
      const hidden = counts[column] === 0 && !showsEmptyColumns(store) && store.view === "board";
      chip.append(
        el("span", "dot"),
        el("span", "summary-label", columnTitle(column, store.payload.done_days)),
        el("strong", "", formatCount(counts[column])),
      );
      if (hidden) {
        chip.append(el("span", "muted", "· hidden"));
        chip.title = "Empty: shown with Display > Show empty columns";
      }
      chip.addEventListener("click", () => {
        if (hidden) {
          store.showEmpty = true;
          requestRender();
          return;
        }
        setView(target.view, target.column);
      });
      return chip;
    }),
  );
}
