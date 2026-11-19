// The history or change entries the rules keep: a Kind or Author rule
// keeps an entry of one of its values ("any") or of none ("not"); a Field
// rule keeps only the changes and lines of its fields ("any") or all but
// theirs ("not"), and drops an entry left with none. An entry without an
// author counts as "" (Unknown).
export function filterEntries(entries, rules) {
  const kept = [];
  for (const entry of entries) {
    let shown = entry;
    let keep = true;
    for (const rule of rules) {
      const wanted = rule.op !== "not";
      if (rule.field === "field") {
        const changes = shown.changes.filter((change) => rule.values.includes(change.field) === wanted);
        const lines = shown.lines.filter((line) => rule.values.includes(line.field) === wanted);
        shown = { ...shown, changes, lines };
        keep &&= changes.length + lines.length > 0;
      } else {
        const value = rule.field === "event" ? entry.event : (entry.author ?? "");
        keep &&= rule.values.includes(value) === wanted;
      }
    }
    if (keep) {
      kept.push(shown);
    }
  }
  return kept;
}
