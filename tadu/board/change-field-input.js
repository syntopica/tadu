import { capitalize } from "./capitalize.js";
import { el } from "./el.js";
import { requestRender } from "./request-render.js";

// One labelled input of the change dialog; typing updates `values` in place
// (no render), so the dialog keeps its focus, and a finished change renders
// again (a new repository shows the fields of its format). A choice, shown
// capitalised unless the field is `plain` (names such as repositories), may
// be left unset unless the form needs it.
export function changeFieldInput(field, values) {
  const label = el("label", field.wide ? "change-field wide" : "change-field");
  label.field = field;
  label.append(el("span", "field-label", field.required ? `${field.label} *` : field.label));
  let input;
  if (field.input === "select") {
    input = el("select");
    const unset = field.required ? [] : [["", "—"]];
    for (const [value, text] of [...unset, ...field.choices.map((choice) => [choice, field.plain ? choice : capitalize(choice)])]) {
      const option = el("option", "", text);
      option.value = value;
      option.selected = value === values[field.name];
      input.append(option);
    }
  } else {
    input = el("input");
    input.type = { date: "date", number: "number" }[field.input] ?? "text";
    input.autocomplete = "off";
  }
  input.name = field.name;
  input.value = values[field.name];
  input.required = field.required;
  input.addEventListener("input", () => {
    values[field.name] = input.value;
  });
  input.addEventListener("change", () => {
    values[field.name] = input.value;
    requestRender();
  });
  label.append(input);
  if (field.hint) {
    const hint = el("span", "field-hint", field.hint);
    hint.id = `change-${field.name}-${field.format ?? 0}-hint`;
    input.setAttribute("aria-describedby", hint.id);
    label.append(hint);
  }
  return label;
}
