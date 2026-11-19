import { el } from "./el.js";
import { externalLink } from "./external-link.js";
import { inlineTitle } from "./inline-title.js";
import { safeRemote } from "./safe-remote.js";

// One text field of a task as `kind` reads it (see TASK_TEXT_FIELDS): a
// line, Markdown lines with a gap for each blank one, a point per line, or
// a list of links (https ones followed) or paths. Text stays text: **bold**
// and `code` are the only Markdown drawn.
export function taskTextValue(kind, value) {
  const lines = (Array.isArray(value) ? value : [value]).map(String);
  if (kind === "line" || kind === "text") {
    const block = el("div", "task-text");
    for (const line of lines) {
      const row = el("p", line.trim() === "" ? "task-gap" : "");
      row.append(inlineTitle(line));
      block.append(row);
    }
    return block;
  }
  const list = el("ul", `task-${kind}`);
  for (const line of lines.filter((text) => text.trim() !== "")) {
    const item = el("li", kind === "paths" ? "mono" : "");
    if (kind === "links" && safeRemote(line, window.location.href)) {
      item.append(externalLink(line, line, "task-link"));
    } else if (kind === "points") {
      item.append(inlineTitle(line.replace(/^\s*[-*]\s+/, "")));
    } else {
      item.append(line);
    }
    list.append(item);
  }
  return list;
}
