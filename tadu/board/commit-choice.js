import { distinctValues } from "./distinct-values.js";
import { requestRender } from "./request-render.js";
import { resolveChoice } from "./resolve-choice.js";
import { store } from "./store.js";

// Apply what was typed into the `name` filter field when it names one value;
// otherwise leave the filter as it was and mark the field. `final` is true
// when the person has finished (change event), false while typing.
export function commitChoice(name, input, final) {
  const value = resolveChoice(input.value, distinctValues(store.cards, name));
  if (value === null) {
    input.classList.toggle("invalid", final);
    return;
  }
  input.classList.remove("invalid");
  if (final) {
    input.value = value;
  }
  if (
    value !== store.filters[name] &&
    (final || value === input.value.trim())
  ) {
    store.filters = { ...store.filters, [name]: value };
    requestRender();
  }
}
