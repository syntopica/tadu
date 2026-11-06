import { renderPicker } from "./render-picker.js";
import { store } from "./store.js";

// Open the scope picker of one level ("company", "project", "repository")
// under the control that asked for it, or the keyboard switcher of every
// level ("switcher", no anchor) near the top of the page.
export function openPicker(kind, anchor) {
  if (!store.index) {
    return;
  }
  store.picker?.anchor?.setAttribute("aria-expanded", "false");
  store.picker = { kind, anchor, active: 0, options: [] };
  const picker = document.getElementById("picker");
  const input = document.getElementById("picker-input");
  input.value = "";
  input.placeholder = {
    company: "Search companies...",
    project: "Search projects...",
    repository: "Search repositories...",
  }[kind] ?? "Go to a company, project or repository...";
  picker.classList.toggle("switcher", anchor === null);
  if (anchor !== null) {
    const rect = anchor.getBoundingClientRect();
    const left = Math.max(8, Math.min(rect.left, window.innerWidth - 348));
    picker.style.setProperty("--picker-top", `${Math.round(rect.bottom + 6)}px`);
    picker.style.setProperty("--picker-left", `${Math.round(left)}px`);
    anchor.setAttribute("aria-expanded", "true");
  }
  picker.hidden = false;
  renderPicker(store);
  input.focus();
}
