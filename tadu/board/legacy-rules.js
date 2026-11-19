// The rules a filter choice saved before rules existed stands for: each
// one-value filter as "any" of it, Due before and Overdue as due values,
// Unassigned and No priority as "empty", an organization with its role as
// a relation, and a state as State. An organization or role alone has no
// rule now and is dropped.
export function legacyRules(raw) {
  const rules = [];
  const text = (key) => (typeof raw[key] === "string" ? raw[key] : "");
  const add = (field, op, values) => rules.push({ field, op, values });
  for (const field of ["assignee", "priority", "label", "kind", "category", "type", "milestone"]) {
    if (text(field) !== "") {
      add(field, "any", [text(field)]);
    }
  }
  if (raw.unassigned === true && text("assignee") === "") {
    add("assignee", "empty", []);
  }
  if (raw.noPriority === true && text("priority") === "") {
    add("priority", "empty", []);
  }
  const due = [...(raw.overdue === true ? ["overdue"] : []), ...(text("dueBefore") ? [`before:${text("dueBefore")}`] : [])];
  if (due.length > 0) {
    add("due", "any", due);
  }
  if (text("organization") !== "" && text("role") !== "") {
    add("organization", "any", [`${text("role")}:${text("organization")}`]);
  }
  if (text("column") !== "") {
    add("state", "any", [text("column")]);
  }
  return rules;
}
