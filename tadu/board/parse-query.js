import { QUERY_NAMES } from "./query-names.js";

// The typed filters in a search text, and the text left without them. A
// filter is a word "name:value[,value]" ("-name:" for "is not",
// "name:none" for "is empty"), "is:overdue", "is:unassigned", "is:mine" or
// "is:waiting". Only words followed by a space count until `final` (Enter),
// so a word being typed is not taken half-way. `value(field, typed)` gives
// a field's value or null; a word it cannot read stays in the text.
export function parseQuery(text, final, value) {
  const words = text.split(/(\s+)/);
  const found = [];
  const kept = [];
  const is = {
    overdue: { field: "due", op: "any", values: ["overdue"] },
    unassigned: { field: "assignee", op: "empty", values: [] },
    mine: { field: "assignee", op: "any", values: ["@me"] },
    waiting: { toggle: "waitingOnMe" },
  };
  words.forEach((word, at) => {
    const complete = final || at < words.length - 1;
    const match = /^(-?)([a-z][a-z_-]*):(.+)$/i.exec(word);
    const name = match?.[2].toLowerCase();
    let filter = null;
    if (complete && match && name === "is" && match[1] === "") {
      filter = Object.hasOwn(is, match[3].toLowerCase()) ? is[match[3].toLowerCase()] : null;
    } else if (complete && match && Object.hasOwn(QUERY_NAMES, name)) {
      const field = QUERY_NAMES[name];
      const values = match[3].toLowerCase() === "none" ? [] : match[3].split(",").map((typed) => value(field, typed));
      const op = values.length === 0 ? "empty" : match[1] === "-" ? "not" : "any";
      filter = values.includes(null) ? null : { field, op, values };
    }
    if (filter === null) {
      kept.push(word);
    } else {
      found.push(filter);
    }
  });
  const rest = kept.join("").replace(/\s{2,}/g, " ");
  return { filters: found, text: final ? rest.trim() : rest.replace(/^\s+/, "") };
}
