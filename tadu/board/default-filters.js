// The filter choice with nothing selected; copy it before changing it. The
// company, project and repository are the scope (store.where), not filters.
export const DEFAULT_FILTERS = Object.freeze({
  organization: "",
  role: "",
  assignee: "",
  priority: "",
  label: "",
  dueBefore: "",
  unassigned: false,
  noPriority: false,
  waitingOnMe: false,
  showCancelled: false,
  column: "",
});
