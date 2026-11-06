import { el } from "./el.js";

// One of the Blocked view's All / Blocked for me / Unassigned chips.
export function scopeChip(label, active, onClick) {
  const chip = el("button", "scope-chip", label);
  chip.type = "button";
  chip.setAttribute("aria-pressed", String(active));
  chip.addEventListener("click", onClick);
  return chip;
}
