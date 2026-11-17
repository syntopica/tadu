import { el } from "./el.js";
import { formatCount } from "./format-count.js";
import { icon } from "./icon.js";

// A sidebar or bottom-nav button; `active` marks the current place and a
// `count`, when given, shows after the label.
export function navItem(label, iconName, active, onClick, count = null) {
  const button = el("button", "nav-item");
  button.type = "button";
  button.classList.toggle("active", active);
  if (active) {
    button.setAttribute("aria-current", "page");
  }
  button.append(icon(iconName), el("span", "nav-label", label));
  if (count !== null) {
    button.append(el("span", "nav-count", formatCount(count)));
  }
  button.addEventListener("click", onClick);
  return button;
}
