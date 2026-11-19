import { changeFacts } from "./change-facts.js";
import { el } from "./el.js";
import { inlineTitle } from "./inline-title.js";

// The grouped changes: a heading per kind with its count and who made them,
// then a row per change, newest first. A row whose item is on the board
// carries its key, so a click on it (or its title) opens its detail.
export function changesList(groups, byKey) {
  const list = el("div", "change-groups");
  for (const group of groups) {
    const section = el("section", "change-group");
    const head = el("h2", "change-group-head");
    const who = group.authors.map(([name, count]) => `${name || "Unknown"} ${count}`).join(", ");
    head.append(el("span", "", `${group.title} (${group.count})`), el("span", "muted", who));
    const rows = el("ul", "change-rows");
    for (const entry of group.entries) {
      const row = el("li", "change-row");
      // The title of an item on the board is a button, so the keyboard reaches it too.
      const linked = entry.key !== null && byKey.has(entry.key);
      const title = el(linked ? "button" : "span", "change-title");
      if (linked) {
        row.dataset.key = entry.key;
        title.type = "button";
      }
      const where = `${entry.repository}:${entry.key === null ? entry.path : entry.key.slice(0, 10)}`;
      title.append(inlineTitle(entry.title));
      row.append(
        el("span", "change-day mono", (entry.date ?? "").slice(0, 10)),
        el("span", "change-author", entry.author ?? ""),
        el("span", "change-where mono", where),
        title,
        el("span", "change-facts muted", changeFacts(entry)),
      );
      rows.append(row);
    }
    section.append(head, rows);
    list.append(section);
  }
  return list;
}
