import { el } from "./el.js";
import { icon } from "./icon.js";

// A sidebar or bottom-nav button; `active` marks the current place.
export function navItem(label, iconName, active, onClick) {
  const button = el("button", "nav-item");
  button.type = "button";
  button.classList.toggle("active", active);
  if (active) {
    button.setAttribute("aria-current", "page");
  }
  button.append(icon(iconName), el("span", "nav-label", label));
  button.addEventListener("click", onClick);
  return button;
}
