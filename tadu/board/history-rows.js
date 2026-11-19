// The lines of one history entry, as `tadu show --history` prints them under
// its header: each change as `field: before → after` (`field: value` for a new
// item), then the other lines added (+) and removed (-), a task file's with
// the field they belong to.
export function historyRows(entry) {
  const rows = [];
  if (entry.created) {
    rows.push({ kind: "note", text: `created in ${entry.path}` });
  }
  for (const change of entry.changes) {
    if (!entry.created) {
      const before = change.before ?? "none";
      rows.push({ kind: "field", text: `${change.field}: ${before} → ${change.after ?? "none"}` });
    } else if (change.field !== "file") {
      rows.push({ kind: "field", text: `${change.field}: ${change.after}` });
    }
  }
  for (const line of entry.lines) {
    const text = line.text.replace(/^ {2}/, "");
    const shown = line.field === "text" ? text : `${line.field}: ${text}`;
    rows.push({ kind: line.op === "+" ? "added" : "removed", text: `${line.op} ${shown}` });
  }
  return rows.length > 0 ? rows : [{ kind: "note", text: "(spacing only)" }];
}
