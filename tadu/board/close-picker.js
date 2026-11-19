import { setPlaces } from "./set-places.js";
import { store } from "./store.js";

// Close the scope picker; `refocus` returns focus to the control that
// opened it. Places ticked while it was open join the recent scopes now,
// as one choice.
export function closePicker(refocus) {
  if (store.picker === null) {
    return;
  }
  const { anchor, ticked } = store.picker;
  store.picker = null;
  document.getElementById("picker").hidden = true;
  anchor?.setAttribute("aria-expanded", "false");
  if (ticked) {
    setPlaces(store.places);
  }
  if (refocus) {
    anchor?.focus();
  }
}
