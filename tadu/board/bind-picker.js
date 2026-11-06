import { closePicker } from "./close-picker.js";
import { openPicker } from "./open-picker.js";
import { renderPicker } from "./render-picker.js";
import { setWhere } from "./set-where.js";

// Wire the scope pickers: every [data-picker] control opens its level,
// typing narrows, arrows move, Enter or a click chooses, Esc and Tab close,
// and a click elsewhere closes.
export function bindPicker(store) {
  const input = document.getElementById("picker-input");
  const list = document.getElementById("picker-list");
  const choose = (at) => {
    const option = store.picker?.options[at];
    if (option) {
      closePicker(true);
      setWhere(option.target);
    }
  };
  document.addEventListener("click", (event) => {
    const trigger = event.target.closest?.("[data-picker]");
    if (trigger) {
      const same = store.picker?.anchor === trigger;
      closePicker(false);
      if (!same) {
        openPicker(trigger.dataset.picker, trigger);
      }
    } else if (store.picker && !event.target.closest?.("#picker")) {
      closePicker(false);
    }
  });
  input.addEventListener("input", () => {
    store.picker.active = 0;
    renderPicker(store);
  });
  input.addEventListener("keydown", (event) => {
    const step = { ArrowDown: 1, ArrowUp: -1 }[event.key];
    if (step !== undefined) {
      event.preventDefault();
      store.picker.active += step;
      renderPicker(store);
    } else if (event.key === "Enter") {
      event.preventDefault();
      choose(store.picker.active);
    } else if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      closePicker(true);
    } else if (event.key === "Tab") {
      closePicker(false);
    }
  });
  list.addEventListener("mousedown", (event) => event.preventDefault());
  list.addEventListener("click", (event) => {
    const item = event.target.closest?.("[data-at]");
    if (item) {
      choose(Number(item.dataset.at));
    }
  });
}
