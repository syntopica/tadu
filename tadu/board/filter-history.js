// The history entries a filter keeps, by the rules of `tadu show` (Python's
// filter_history): within the days (inclusive, by the commit's own day;
// uncommitted changes count as `today`) and by an author whose name contains
// the text; with fields, only their changes and lines, dropping an entry left
// with none.
export function filterHistory(entries, filter, today) {
  const until = filter.until || "9999-12-31";
  const author = filter.author.toLowerCase();
  const kept = [];
  for (const entry of entries) {
    const day = entry.date ? entry.date.slice(0, 10) : today;
    const by = (entry.author ?? "").toLowerCase();
    if (day < filter.since || day > until || (author && !by.includes(author))) {
      continue;
    }
    if (filter.fields.length === 0) {
      kept.push(entry);
      continue;
    }
    const changes = entry.changes.filter((change) => filter.fields.includes(change.field));
    const lines = entry.lines.filter((line) => filter.fields.includes(line.field));
    if (changes.length > 0 || lines.length > 0) {
      kept.push({ ...entry, changes, lines });
    }
  }
  return kept;
}
