// Close every open popover (Display, a day range) but the one inside
// `keep`, keeping aria-expanded on their buttons in step.
export function closePopovers(keep = null) {
  for (const popover of document.querySelectorAll(".popover")) {
    const anchor = popover.closest(".popover-anchor");
    if (!popover.hidden && anchor !== keep) {
      popover.hidden = true;
      anchor?.querySelector("[aria-expanded]")?.setAttribute("aria-expanded", "false");
    }
  }
}
