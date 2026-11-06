import { store } from "./store.js";

// Close the scope picker; `refocus` returns focus to the control that
// opened it.
export function closePicker(refocus) {
  if (store.picker === null) {
    return;
  }
  const anchor = store.picker.anchor;
  store.picker = null;
  document.getElementById("picker").hidden = true;
  anchor?.setAttribute("aria-expanded", "false");
  if (refocus) {
    anchor?.focus();
  }
}
