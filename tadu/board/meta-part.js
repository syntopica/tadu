import { el } from "./el.js";
import { icon } from "./icon.js";

// One icon-and-text piece of a card's context line.
export function metaPart(iconName, text, className = "") {
  const part = el("span", `meta-part ${className}`.trim());
  part.title = text;
  part.append(icon(iconName), el("span", "meta-text", text));
  return part;
}
