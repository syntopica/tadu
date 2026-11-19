import { requestRender } from "./request-render.js";
import { runChange } from "./run-change.js";

// Open the change dialog for a spec (see cardActions), its fields at their
// starting values, remembering what opened it (the control, else what had
// the focus: a click does not focus a button in every browser). A spec without fields
// applies at once, and the dialog shows only if tadu refuses it.
export function openChange(store, spec, opener = document.activeElement) {
  const values = Object.fromEntries(spec.fields.map((field) => [field.name, String(field.value ?? "")]));
  const direct = spec.fields.length === 0;
  store.change = { spec, values, output: "", error: "", busy: false, similar: [], direct, opener };
  if (direct) {
    runChange(store, false);
    return;
  }
  requestRender();
}
