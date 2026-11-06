// The values a card offers to each single-value filter.
export const FILTER_VALUES = {
  repository: (card) => [card.repository],
  project: (card) => (card.project === null ? [] : [card.project]),
  organization: (card) => card.organizations.map((entry) => entry.org),
  role: (card) => card.organizations.map((entry) => entry.role),
  assignee: (card) => card.assignees,
  priority: (card) => (card.priority === null ? [] : [card.priority]),
  label: (card) => card.labels,
};
