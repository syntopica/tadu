import { el } from "./el.js";

// Replace a select's options with [value, label] pairs and select `value`
// (or the first option when it is no longer offered).
export function fillSelect(select, options, value) {
  select.replaceChildren(
    ...options.map(([optionValue, label]) => {
      const option = el("option", "", label);
      option.value = optionValue;
      return option;
    }),
  );
  select.value = options.some(([optionValue]) => optionValue === value)
    ? value
    : (options[0]?.[0] ?? "");
}
