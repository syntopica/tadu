import { CHANGE_EVENTS } from "./change-events.js";
import { filterEntries } from "./filter-entries.js";

// The values the Filter menu offers for a Changes or History field, each
// {value, label, count} with how many entries it keeps: the kinds in the
// order `tadu changes` groups them, authors by name, fields in the order
// they first changed (the entry that created an item aside: it names every
// field it set). A value already `chosen` stays, so it can be turned off.
export function entryValues(entries, field, chosen) {
  let values;
  if (field === "event") {
    values = CHANGE_EVENTS.map(([event]) => event).filter((event) => entries.some((entry) => entry.event === event));
  } else if (field === "author") {
    values = [...new Set(entries.map((entry) => entry.author ?? ""))].sort();
  } else {
    const changed = entries.filter((entry) => !entry.created);
    values = [...new Set(changed.flatMap((entry) => [...entry.changes, ...entry.lines].map((item) => item.field)))];
  }
  values = [...values, ...chosen.filter((value) => !values.includes(value))];
  const titles = Object.fromEntries(CHANGE_EVENTS);
  const label = (value) =>
    ({ event: titles[value] ?? value, author: value || "Unknown", field: value.replaceAll("_", " ") })[field];
  return values.map((value) => ({
    value,
    label: label(value),
    count: filterEntries(entries, [{ field, op: "any", values: [value] }]).length,
  }));
}
