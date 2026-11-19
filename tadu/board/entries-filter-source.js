import { CHANGE_FIELDS } from "./change-fields.js";
import { entryValues } from "./entry-values.js";

// What the Filter menu filters in the Changes view or an item's History:
// `fields` (the CHANGE_FIELDS keys offered), the `entries` read (a
// function, as they load later), and the rules with how to change them.
export function entriesFilterSource(fields, entries, rules, change) {
  return {
    fields: () => CHANGE_FIELDS.filter((field) => fields.includes(field.key)),
    values: (field, chosen) => entryValues(entries(), field, chosen),
    quick: () => [],
    rules,
    change,
  };
}
