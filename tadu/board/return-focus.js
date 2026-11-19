// Give the focus back when the change dialog closes: to what opened it;
// when a reload rebuilt that, to the same action in the detail, else to the
// detail's Close, else to the page's content.
export function returnFocus(opener) {
  if (opener?.isConnected) {
    opener.focus();
    return;
  }
  const detail = document.getElementById("detail");
  const action = opener?.dataset?.action;
  const again = action ? detail.querySelector(`[data-action="${action}"]`) : null;
  const close = detail.querySelector("button.icon-button");
  const target = detail.hidden ? null : (again ?? close);
  (target ?? document.getElementById("content")).focus();
}
