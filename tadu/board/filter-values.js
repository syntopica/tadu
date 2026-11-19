// The values a card offers to each filter field but the due date, whose
// presets depend on the day (see dueTags): its state (board column), each
// "role:org" it is related by, and the fields themselves.
export const FILTER_VALUES = {
  state: (card) => [card.column],
  assignee: (card) => card.assignees,
  priority: (card) => (card.priority === null ? [] : [card.priority]),
  label: (card) => card.labels,
  kind: (card) => [card.kind ?? "unclassified"],
  category: (card) => (card.category ? [card.category] : []),
  type: (card) => (card.type ? [card.type] : []),
  milestone: (card) => (card.milestone ? [card.milestone] : []),
  organization: (card) => card.organizations.map((entry) => `${entry.role}:${entry.org}`),
};
