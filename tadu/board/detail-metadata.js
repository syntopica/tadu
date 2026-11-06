import { el } from "./el.js";
import { icon } from "./icon.js";

// The raw facts behind an item, folded by default.
export function detailMetadata(card) {
  const details = el("details", "metadata");
  const summary = el("summary");
  summary.append(
    icon("info"),
    el("span", "", "Metadata"),
    icon("chevronDown", "icon summary-chevron"),
  );
  const list = el("dl", "fields");
  const span = card.end_line > card.line ? `${card.line}-${card.end_line}` : String(card.line);
  for (const [label, value] of [
    ["Key", card.key],
    ["Stable ID", card.stable ? "Yes" : "No (derived key, unstable)"],
    ["Path", card.path],
    ["Lines", span],
    ["Queue", card.queue ?? "—"],
    ["Estimate", card.estimate ?? "—"],
    ["Closing day", card.day ?? "—"],
  ]) {
    list.append(el("dt", "", label), el("dd", "mono", value));
  }
  details.append(summary, list);
  return details;
}
