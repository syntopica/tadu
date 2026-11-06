import { el } from "./el.js";

// Offer `values` as the suggestions of a typed filter field, each with its
// display name from `names` when it has one, and show `value`, unless the
// person is typing in it right now.
export function fillChoice(input, values, value, names = new Map()) {
  const list = document.getElementById(input.getAttribute("list"));
  list.replaceChildren(
    ...values.map((offered) => {
      const option = el("option");
      option.value = offered;
      if (names.has(offered)) {
        option.label = names.get(offered);
      }
      return option;
    }),
  );
  if (document.activeElement !== input) {
    input.value = value;
    input.classList.remove("invalid");
  }
}
