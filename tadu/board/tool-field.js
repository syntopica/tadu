// One field of a change form, from the tool's own input schema (the board
// gets it with the cards): a choice offers the schema's values, a number
// takes whole numbers, a list takes comma-separated values. `options` may
// set `input` (date for a string; line for a list given one whole line at
// a time, such as a note), `required`, the starting `value`, a `hint` shown
// under the field, `wide` for a field across the form, and `format` for a
// field only one backlog format takes (1 or 2).
export function toolField(tools, operation, name, label, options = {}) {
  const property = tools?.[operation]?.properties?.[name] ?? { type: "string" };
  const input = property.enum
    ? "select"
    : options.input ?? { integer: "number", array: "list" }[property.type] ?? "text";
  return {
    name,
    label,
    input,
    choices: property.enum ?? [],
    hint: options.hint ?? "",
    required: options.required ?? false,
    value: options.value ?? "",
    wide: options.wide ?? false,
    format: options.format ?? 0,
  };
}
