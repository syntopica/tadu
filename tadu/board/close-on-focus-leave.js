// Call `close` when the focus leaves `popup` for good: Tab moves through
// its controls, and a control drawn anew under the focus (a popup redraws
// itself after a click) does not count as leaving, since the popup puts the
// focus back first.
export function closeOnFocusLeave(popup, isOpen, close) {
  popup.addEventListener("focusout", () => {
    setTimeout(() => {
      if (isOpen() && !popup.contains(document.activeElement)) {
        close();
      }
    }, 0);
  });
}
