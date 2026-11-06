import { el } from "./el.js";
import { icon } from "./icon.js";

// One label and value pair of the detail grid; `value` is a string or nodes.
export function detailField(label, iconName, value) {
  const term = el("dt", "", label);
  const description = el("dd");
  if (iconName) {
    description.append(icon(iconName));
  }
  if (typeof value === "string") {
    description.append(el("span", value === "—" ? "muted" : "", value));
  } else {
    description.append(...value);
  }
  return [term, description];
}
