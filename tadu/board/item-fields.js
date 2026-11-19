// The properties an item list filters by, in the order the Filter menu
// offers them: each with its title, icon and the ways it may match.
export const ITEM_FIELDS = [
  { key: "state", title: "State", icon: "columns", ops: ["any", "not"] },
  { key: "assignee", title: "Assignee", icon: "user", ops: ["any", "not", "empty"] },
  { key: "priority", title: "Priority", icon: "bolt", ops: ["any", "not", "empty"] },
  { key: "label", title: "Label", icon: "tag", ops: ["any", "not", "empty"] },
  { key: "due", title: "Due date", icon: "calendar", ops: ["any", "not", "empty"] },
  { key: "kind", title: "Kind", icon: "layers", ops: ["any", "not"] },
  { key: "category", title: "Category", icon: "folder", ops: ["any", "not", "empty"] },
  { key: "type", title: "Type", icon: "tag", ops: ["any", "not", "empty"] },
  { key: "milestone", title: "Milestone", icon: "bookmark", ops: ["any", "not", "empty"] },
  { key: "organization", title: "Organization", icon: "building", ops: ["any", "not"] },
];
