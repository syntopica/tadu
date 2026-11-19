import { fieldFits } from "./field-fits.js";

// The call's arguments: the spec's own, then each field a person filled in
// or changed, as the tool takes it: trimmed text, a list split on commas,
// one line as a list of it, a number as a number. A field left as it started
// is left out, unless the form needs it, and so is one the chosen
// repository's format does not take (see fieldFits).
export function changeArguments(spec, values) {
  const args = { ...spec.args };
  for (const field of spec.fields) {
    const raw = String(values[field.name] ?? "").trim();
    const unchanged = !field.required && raw === String(field.value ?? "").trim();
    if (raw === "" || unchanged || !fieldFits(spec, values, field)) {
      continue;
    }
    if (field.input === "list") {
      args[field.name] = raw.split(",").map((part) => part.trim()).filter(Boolean);
    } else if (field.input === "line") {
      args[field.name] = [raw];
    } else {
      args[field.name] = field.input === "number" ? Number(raw) : raw;
    }
  }
  return args;
}
