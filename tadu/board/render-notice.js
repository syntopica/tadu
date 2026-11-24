import { el } from "./el.js";
import { icon } from "./icon.js";
import { noticeLine } from "./notice-line.js";
import { requestRender } from "./request-render.js";

// The line that says a change was made, announced as a status, with a
// button that dismisses it; hidden when there is none.
export function renderNotice(store) {
  const notice = document.getElementById("notice");
  notice.hidden = store.notice === "";
  if (notice.shownText === store.notice) {
    return;
  }
  notice.shownText = store.notice;
  const dismiss = el("button", "icon-button small");
  dismiss.type = "button";
  dismiss.setAttribute("aria-label", "Dismiss");
  dismiss.append(icon("close"));
  dismiss.addEventListener("click", () => {
    store.notice = "";
    requestRender();
  });
  notice.replaceChildren(noticeLine(store.notice), ...(store.notice === "" ? [] : [dismiss]));
}
