import { el } from "./el.js";
import { foldedSummary } from "./folded-summary.js";
import { loadHistory } from "./load-history.js";

// The item's git history, folded; it is fetched only when first opened, and
// again when the panel is rebuilt with the section open (after a reload).
// `filter` carries the filter over such a rebuild; a new item starts with none.
export function detailHistory(card, open, filter) {
  const section = el("details", "metadata history");
  section.historyFilter = filter ?? { since: "", until: "", rules: [] };
  const body = el("div", "history-body");
  section.append(foldedSummary("clock", "History"), body);
  const load = () => {
    if (section.open && section.dataset.loaded === undefined) {
      section.dataset.loaded = "";
      loadHistory(section, body, card);
    }
  };
  section.addEventListener("toggle", load);
  section.open = open;
  load();
  return section;
}
