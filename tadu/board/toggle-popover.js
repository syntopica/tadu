// Open or close the filters popover, keeping aria-expanded in step.
export function togglePopover(open) {
  const button = document.getElementById("filters-button");
  const popover = document.getElementById("filters-popover");
  popover.hidden = !open;
  button.setAttribute("aria-expanded", String(open));
}
