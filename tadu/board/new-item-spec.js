import { canChange } from "./can-change.js";
import { cleanWhere } from "./clean-where.js";
import { placeCovers } from "./place-covers.js";
import { toolField } from "./tool-field.js";

// The change that adds an item to a repository the page may change: the
// first one inside the chosen places, else the first. Kind and the
// section apply to a TODO.md backlog, type and the category slug to a task
// backlog: the form shows those of the chosen repository's format
// (`formats`). Null when no repository may be changed.
export function newItemSpec(payload, places, index) {
  const repositories = (payload?.workspace?.repositories ?? [])
    .map((entry) => entry.key)
    .filter((key) => canChange(payload, key));
  if (repositories.length === 0) {
    return null;
  }
  const field = (name, label, options) => toolField(payload.tools, "add", name, label, options);
  const inside = repositories.filter((key) =>
    places.some((place) => placeCovers(place, cleanWhere({ repository: key }, index), index)),
  );
  const chosen = inside[0] ?? repositories[0];
  return {
    title: "New item",
    operation: "add",
    args: {},
    similar: true,
    formats: payload.formats ?? {},
    fields: [
      { ...field("repository", "Repository"), input: "select", choices: repositories, required: true, value: chosen, plain: true },
      field("title", "Title", { required: true, hint: "One line, imperative" }),
      field("priority", "Priority"),
      field("kind", "Kind", { format: 1 }),
      field("type", "Type", { format: 2, hint: "A type slug of the backlog" }),
      field("category", "Category", { format: 1, hint: "The ## section it goes under" }),
      field("category", "Category", { format: 2, hint: "A category slug of the backlog" }),
      field("due", "Due", { input: "date" }),
      field("assignees", "Assignees", { hint: "Person ids, comma-separated" }),
      field("labels", "Labels", { hint: "Comma-separated" }),
      field("note", "Note", { input: "line", wide: true, hint: "A paragraph under the title" }),
    ],
  };
}
