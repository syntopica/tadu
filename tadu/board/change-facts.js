import { lineFacts } from "./line-facts.js";

// What a change line adds after the title, as `tadu changes` prints it: how
// a reopened item's state went, or every field of a changed one but `file`
// and how many lines of each field it added and removed; nothing for the
// other events.
export function changeFacts(entry) {
  const shown = { reopened: ["state"], changed: null };
  if (!(entry.event in shown)) {
    return "";
  }
  const fields = shown[entry.event];
  const facts = entry.changes
    .filter((change) => change.field !== "file" && (fields === null || fields.includes(change.field)))
    .map((change) => `${change.field}: ${change.before || "none"} → ${change.after || "none"}`);
  return [...facts, ...(fields === null ? lineFacts(entry.lines) : [])].join("; ");
}
