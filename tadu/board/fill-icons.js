import { icon } from "./icon.js";

// Draw the icons the static page asks for with data-icon placeholders.
export function fillIcons(root) {
  for (const node of root.querySelectorAll("[data-icon]")) {
    node.replaceChildren(icon(node.dataset.icon));
  }
}
