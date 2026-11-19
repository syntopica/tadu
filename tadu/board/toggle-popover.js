// Open or close the Display popover, keeping aria-expanded in step.
export function togglePopover(open) {
  const button = document.getElementById("display-button");
  const popover = document.getElementById("display-popover");
  popover.hidden = !open;
  button.setAttribute("aria-expanded", String(open));
}
