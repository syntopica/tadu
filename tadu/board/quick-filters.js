// The one-click filters the Filter menu lists first: each sets one rule
// ("@me" stands for the board's person) or, for Waiting on me, the toggle
// of the same name. Those that need a person show only when the board
// knows who `me` is.
export const QUICK_FILTERS = [
  { key: "mine", title: "Assigned to me", icon: "user", me: true, rule: { field: "assignee", op: "any", values: ["@me"] } },
  { key: "waiting", title: "Waiting on me", icon: "clock", me: true, toggle: "waitingOnMe" },
  { key: "overdue", title: "Overdue", icon: "calendar", me: false, rule: { field: "due", op: "any", values: ["overdue"] } },
  { key: "unassigned", title: "Unassigned", icon: "users", me: false, rule: { field: "assignee", op: "empty", values: [] } },
  { key: "unprioritized", title: "No priority", icon: "bolt", me: false, rule: { field: "priority", op: "empty", values: [] } },
];
