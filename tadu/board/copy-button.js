import { el } from "./el.js";
import { icon } from "./icon.js";

// An icon button that copies `value` to the clipboard and says so.
export function copyButton(value, label) {
  const button = el("button", "icon-button small");
  button.type = "button";
  button.setAttribute("aria-label", label);
  button.title = label;
  button.append(icon("copy"));
  button.addEventListener("click", async (event) => {
    event.stopPropagation();
    try {
      await navigator.clipboard.writeText(value);
      button.title = "Copied";
      button.classList.add("copied");
    } catch {
      button.title = "Copy failed: select the text instead";
    }
  });
  return button;
}
