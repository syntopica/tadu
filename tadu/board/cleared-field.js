// The first field of a change that held a value and was emptied, or
// undefined: `tadu mark` sets fields but cannot remove one, so emptying it
// would do nothing, while the form seemed to say it would.
export function clearedField(spec, values) {
  return spec.fields.find(
    (field) => String(field.value ?? "").trim() !== "" && String(values[field.name] ?? "").trim() === "",
  );
}
