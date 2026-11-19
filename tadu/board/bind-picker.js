import { bindListClicks } from "./bind-list-clicks.js";
import { closeOnFocusLeave } from "./close-on-focus-leave.js";
import { closePicker } from "./close-picker.js";
import { openPicker } from "./open-picker.js";
import { renderPicker } from "./render-picker.js";
import { setPlaces } from "./set-places.js";
import { togglePlace } from "./toggle-place.js";

// Wire the scope picker: every [data-picker] control opens it; typing
// narrows the tree, the arrows move, Right and Left unfold, fold or step
// in and out; Enter keeps only the active place (or opens a starred or
// recent scope) and closes, Shift+Enter or a click ticks or unticks it and
// stays; Only keeps that place alone. Tab reaches Clear; Esc, and the focus
// or a click going elsewhere, close.
export function bindPicker(store) {
  const input = document.getElementById("picker-input");
  const list = document.getElementById("picker-list");
  const redraw = () => renderPicker(store);
  const only = (row) => {
    store.picker.ticked = false;
    closePicker(true);
    setPlaces(row.kind === "saved" ? row.places : [row.node.place]);
  };
  const tick = (row) => {
    store.picker.ticked = true;
    setPlaces(togglePlace(store.places, row.node.place, store.index), false);
    redraw();
  };
  const fold = (row, unfold) => {
    store.picker.open[unfold ? "add" : "delete"](row.node.key);
    redraw();
  };
  document.addEventListener("click", (event) => {
    const trigger = event.target.closest?.("[data-picker]");
    if (trigger) {
      const same = store.picker?.anchor === trigger;
      closePicker(false);
      if (!same) {
        openPicker(trigger);
      }
    } else if (store.picker && !event.target.closest?.("#picker") && event.target.isConnected !== false) {
      closePicker(false);
    }
  });
  document.getElementById("picker-clear").addEventListener("click", () => {
    setPlaces([], false);
    redraw();
  });
  input.addEventListener("input", () => {
    store.picker.active = 0;
    redraw();
  });
  input.addEventListener("keydown", (event) => {
    const state = store.picker;
    const row = state.rows[state.active];
    const step = { ArrowDown: 1, ArrowUp: -1 }[event.key];
    if (step !== undefined) {
      event.preventDefault();
      state.active += step;
      redraw();
    } else if ((event.key === "ArrowRight" || event.key === "ArrowLeft") && row?.kind === "node" && input.value === "") {
      event.preventDefault();
      const right = event.key === "ArrowRight";
      if (row.folds && row.unfolded !== right) {
        fold(row, right);
      } else {
        const target = right ? state.active + 1 : state.rows.findIndex((other) => other.node?.key === row.parent);
        state.active = target >= 0 && (!right || row.unfolded) ? target : state.active;
        redraw();
      }
    } else if (event.key === "Enter" && row) {
      event.preventDefault();
      if (event.shiftKey && row.kind === "node") {
        tick(row);
      } else {
        only(row);
      }
    } else if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      closePicker(true);
    }
  });
  closeOnFocusLeave(document.getElementById("picker"), () => store.picker !== null, () => closePicker(false));
  bindListClicks(list, (at, event) => {
    if (!store.picker) {
      return;
    }
    store.picker.active = at;
    const row = store.picker.rows[at];
    const action = event.target.closest?.("[data-action]")?.dataset.action;
    if (action === "fold") {
      fold(row, !row.unfolded);
    } else if (action === "only" || row.kind === "saved") {
      only(row);
    } else {
      tick(row);
    }
  });
}
