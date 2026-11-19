import { OPEN_COLUMNS } from "./open-columns.js";
import { toolField } from "./tool-field.js";

// The changes the page offers for an open card, as {key, label, spec}: a
// spec names the operation, its fixed arguments (the card's key and
// repository) and the fields a person fills in; one without fields applies
// at once. Start claims the item for `me` when the workspace has one.
// Closed items offer nothing.
export function cardActions(card, me, tools) {
  if (!OPEN_COLUMNS.includes(card.column)) {
    return [];
  }
  const target = { id: card.key, repository: card.repository };
  const task = card.path.endsWith(".json");
  const field = (operation, name, label, options) => toolField(tools, operation, name, label, options);
  const start = me
    ? { operation: "claim", args: { ...target, who: me }, fields: [] }
    : { operation: "mark", args: { ...target, state: "in_progress" }, fields: [] };
  const actions = [
    ["start", "Start", card.column !== "in_progress" && card.column !== "blocked", start],
    ["unblock", "Unblock", card.column === "blocked", { operation: "mark", args: { ...target, state: "open" }, fields: [] }],
    ["block", "Block…", card.column !== "blocked", {
      operation: "mark",
      args: { ...target, state: "blocked" },
      fields: [field("mark", "note", "What blocks it", { required: true, wide: true })],
    }],
    ["done", "Done…", true, {
      operation: "close",
      args: target,
      fields: [
        field("close", "evidence", "Evidence", {
          required: true,
          wide: true,
          hint: "What proves it is done: a test, a command's result, a commit or a PR",
        }),
        field("close", "result", "Result", { wide: true, hint: "What changed (default: the title)" }),
      ],
    }],
    ["cancel", "Cancel…", true, {
      operation: "close",
      args: target,
      fields: [field("close", "resolution", "Why it no longer applies", { required: true, wide: true })],
    }],
    ["edit", "Edit…", true, {
      operation: "mark",
      args: target,
      fields: [
        field("mark", "priority", "Priority", { value: card.priority ?? "" }),
        field("mark", "assignees", "Assignees", { value: card.assignees.join(", "), hint: "Person ids, comma-separated" }),
        field("mark", "labels", "Labels", { value: card.labels.join(", "), hint: "Comma-separated" }),
        field("mark", "due", "Due", { input: "date", value: card.due ?? "" }),
        field("mark", "not_before", task ? "Defer until" : "Not before", {
          input: "date",
          value: (task ? card.defer_until : card.not_before) ?? "",
        }),
        ...(task ? [] : [
          field("mark", "kind", "Kind", { value: card.kind ?? "" }),
          field("mark", "check_on", "Check on", { input: "date", value: card.check_on ?? "" }),
        ]),
        field("mark", "queue", "Queue", { value: card.queue ?? "" }),
        field("mark", "estimate", "Estimate (minutes)", { value: card.estimate ?? "" }),
        field("mark", "note", "Add a note", { wide: true, hint: "A paragraph added to the item" }),
      ],
    }],
  ];
  return actions
    .filter(([, , offered]) => offered)
    .map(([key, label, , spec]) => ({ key, label, spec: { title: `${label.replace("…", "")}: ${card.title}`, ...spec } }));
}
