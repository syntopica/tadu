import { el } from "./el.js";
import { failureText } from "./failure-text.js";
import { fetchHistory } from "./fetch-history.js";
import { historyView } from "./history-view.js";
import { store } from "./store.js";

// Fill an opened History section, with the section's filter. A failure says
// why and clears the section's loaded mark, so opening it again retries.
export async function loadHistory(section, body, card) {
  body.replaceChildren(el("p", "muted", "Loading the history from git…"));
  try {
    const payload = await fetchHistory(card);
    const today = store.payload.today;
    body.replaceChildren(historyView({ ...payload, today }, section.historyFilter));
  } catch (error) {
    delete section.dataset.loaded;
    body.replaceChildren(el("p", "history-error", failureText(error, "History unavailable")));
  }
}
