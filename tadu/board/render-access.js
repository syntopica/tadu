import { newItemSpec } from "./new-item-spec.js";

// Say what the page may do, as the board was started (`--allow`), and show
// New item only when some repository may be changed.
export function renderAccess(store) {
  const allow = store.payload?.allow ?? "read";
  const label = allow === "read" ? "Read only" : "Can change items";
  const hint =
    allow === "read"
      ? "This board only reads: start it with `tadu board --allow write` to change items here."
      : "Changes go through tadu, as the command line makes them; a repository's access in the workspace can still keep it read only.";
  const access = document.getElementById("access-label");
  access.textContent = label;
  access.title = hint;
  document.getElementById("access-pill").textContent = allow === "read" ? label : "Can change";
  document.getElementById("new-item").hidden = newItemSpec(store.payload, store.places, store.index) === null;
}
