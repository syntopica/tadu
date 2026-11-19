import { callCardRows } from "./call-card-rows.js";
import { CALL_VIEWS } from "./call-views.js";
import { el } from "./el.js";
import { findingRows } from "./finding-rows.js";
import { inlineTitle } from "./inline-title.js";
import { jsonLines } from "./json-lines.js";
import { loadCall } from "./load-call.js";

// A view drawn from one reading tool call (see CALL_VIEWS): asked again
// whenever the board reloads, its rows in the command's own order. Doctor
// lists findings; the others list cards, inside the scope.
export function renderCallView(store, content) {
  const view = store.view;
  const spec = CALL_VIEWS[view];
  const key = `${view}|${store.payload.generated_at}`;
  const state = store.calls[view] ?? {};
  if (state.loadedFor !== key && state.wanted !== key) {
    loadCall(store, view, key);
  }
  const page = el("div", "call-view");
  const intro = el("p", "muted call-intro");
  intro.append(inlineTitle(spec.intro));
  page.append(intro);
  store.navKeys = [];
  if (state.loadedFor !== key) {
    page.append(el("p", "muted", "Asking tadu…"));
  } else if (state.error) {
    page.append(el("p", "history-error", state.error));
  } else {
    const objects = jsonLines(state.payload.output);
    const found = view === "doctor" ? { rows: findingRows(objects), keys: [] } : callCardRows(objects, store);
    store.navKeys = found.keys;
    const list = el("div", view === "doctor" ? "call-findings" : "call-list");
    list.append(...found.rows);
    page.append(found.rows.length > 0 ? list : el("p", "empty-state", spec.empty));
  }
  content.replaceChildren(page);
}
