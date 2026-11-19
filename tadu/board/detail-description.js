import { detailTaskText } from "./detail-task-text.js";
import { el } from "./el.js";
import { icon } from "./icon.js";
import { taskFile } from "./task-file.js";

// The words of an item: a task's text fields, drawn from its file; a
// TODO.md item's Markdown as written.
export function detailDescription(card) {
  const task = taskFile(card);
  if (task !== null) {
    return detailTaskText(task);
  }
  const description = el("section", "description");
  const label = el("h3");
  label.append(icon("text"), el("span", "", "Description"));
  description.append(label, el("pre", "mono", card.text));
  return description;
}
