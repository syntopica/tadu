import { el } from "./el.js";
import { historyHead } from "./history-head.js";
import { historyRows } from "./history-rows.js";

// History entries, newest first; every text is set as text, never as HTML.
// `empty` is what to say when there are none.
export function historyList(entries, empty) {
  if (entries.length === 0) {
    return el("p", "muted", empty);
  }
  const list = el("ol", "history-list");
  for (const entry of entries) {
    const head = historyHead(entry);
    const title = el("div", "history-head");
    title.append(el("span", "history-title", head.title));
    if (head.merge) {
      title.append(el("span", "muted-pill", "merge"));
    }
    const rows = el("ul", "history-rows mono");
    for (const row of historyRows(entry)) {
      rows.append(el("li", `history-${row.kind}`, row.text));
    }
    const item = el("li", entry.commit === null ? "history-entry uncommitted" : "history-entry");
    item.append(title, el("div", "history-detail muted", head.detail), rows);
    list.append(item);
  }
  return list;
}
