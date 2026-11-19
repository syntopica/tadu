import { el } from "./el.js";
import { icon } from "./icon.js";
import { TASK_TEXT_FIELDS } from "./task-text-fields.js";
import { taskTextValue } from "./task-text-value.js";

// The words of a task (format 2) in place of a raw file: its blocker, notes,
// acceptance criteria, result, evidence, links... each under its title, only
// those it has.
export function detailTaskText(task) {
  const section = el("section", "description task-text-fields");
  const heading = (title, iconName) => {
    const label = el("h3");
    label.append(icon(iconName), el("span", "", title));
    return label;
  };
  for (const [key, title, iconName, kind] of TASK_TEXT_FIELDS) {
    const value = task[key];
    if (value !== undefined && value !== null && value !== "" && !(Array.isArray(value) && value.length === 0)) {
      section.append(heading(title, iconName), taskTextValue(kind, value));
    }
  }
  if (section.children.length === 0) {
    section.append(heading("Notes", "text"), el("p", "muted", "No notes yet."));
  }
  return section;
}
