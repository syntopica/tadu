import { bindListClicks } from "./bind-list-clicks.js";
import { chooseMenuOption } from "./choose-menu-option.js";
import { closeFilterMenu } from "./close-filter-menu.js";
import { closeOnFocusLeave } from "./close-on-focus-leave.js";
import { renderFilterMenu } from "./render-filter-menu.js";

// Wire the Filter menu: typing narrows, the arrows move, Enter chooses,
// Backspace in an empty search steps back (or, on the first step, removes
// the last rule), Esc steps back or closes; Tab reaches the ways of matching
// and the foot, and the menu closes when the focus or a click goes
// elsewhere. A control that opens the menu marks itself data-filter-anchor.
export function bindFilterMenu(store) {
  const input = document.getElementById("filter-menu-input");
  const list = document.getElementById("filter-menu-list");
  const back = () => {
    Object.assign(store.menu, { field: null, op: null, active: 0 });
    input.value = "";
    renderFilterMenu(store);
  };
  input.addEventListener("input", () => {
    store.menu.active = 0;
    renderFilterMenu(store);
  });
  input.addEventListener("keydown", (event) => {
    const menu = store.menu;
    const step = { ArrowDown: 1, ArrowUp: -1 }[event.key];
    if (step !== undefined) {
      event.preventDefault();
      menu.active += step;
      renderFilterMenu(store);
    } else if (event.key === "Enter") {
      event.preventDefault();
      const option = menu.options[menu.active];
      if (option) {
        chooseMenuOption(store, option);
      }
    } else if (event.key === "Escape") {
      event.preventDefault();
      event.stopPropagation();
      if (menu.field !== null && !menu.direct) {
        back();
      } else {
        closeFilterMenu(true);
      }
    } else if (event.key === "Backspace" && input.value === "") {
      if (menu.field !== null && !menu.direct) {
        event.preventDefault();
        back();
      } else if (menu.field === null && menu.source.rules().length > 0) {
        event.preventDefault();
        menu.source.change(menu.source.rules().slice(0, -1));
        renderFilterMenu(store);
      }
    }
  });
  closeOnFocusLeave(document.getElementById("filter-menu"), () => store.menu !== null, () => closeFilterMenu(false));
  bindListClicks(list, (at) => {
    if (store.menu) {
      store.menu.active = at;
      chooseMenuOption(store, store.menu.options[at]);
    }
  });
  document.addEventListener("click", (event) => {
    const inside = event.target.closest?.("#filter-menu, [data-filter-anchor]");
    if (store.menu && !inside && event.target.isConnected !== false) {
      closeFilterMenu(false);
    }
  });
}
