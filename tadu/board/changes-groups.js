import { CHANGE_EVENTS } from "./change-events.js";

// Changes grouped by event in the order `tadu changes` prints them, each with
// how many there are and who made them, most first, then by name.
export function changesGroups(entries) {
  const groups = [];
  for (const [event, title] of CHANGE_EVENTS) {
    const found = entries.filter((entry) => entry.event === event);
    if (found.length === 0) {
      continue;
    }
    const counts = new Map();
    for (const entry of found) {
      const author = entry.author ?? "";
      counts.set(author, (counts.get(author) ?? 0) + 1);
    }
    const byName = (a, b) => (a[0] < b[0] ? -1 : Number(a[0] > b[0]));
    const authors = [...counts].sort((a, b) => b[1] - a[1] || byName(a, b));
    groups.push({ event, title, count: found.length, authors, entries: found });
  }
  return groups;
}
