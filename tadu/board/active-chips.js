import { COLUMN_TITLES } from "./column-titles.js";
import { PRIORITY_TITLES } from "./priority-titles.js";

// The active filters as removable chips: {name, label}. The project is the
// top bar's scope, so it is not repeated here.
export function activeChips(filters) {
  const names = {
    repository: "Repository",
    organization: "Organization",
    role: "Role",
    assignee: "Assignee",
    priority: "Priority",
    label: "Label",
  };
  const chips = [];
  for (const [name, title] of Object.entries(names)) {
    if (filters[name] !== "") {
      const value = name === "priority" ? PRIORITY_TITLES[filters[name]] : filters[name];
      chips.push({ name, label: `${title}: ${value}` });
    }
  }
  const toggles = {
    unassigned: "Unassigned",
    noPriority: "No priority",
    waitingOnMe: "Waiting on me",
    showCancelled: "Cancelled shown",
  };
  for (const [name, label] of Object.entries(toggles)) {
    if (filters[name]) {
      chips.push({ name, label });
    }
  }
  if (filters.column !== "") {
    chips.push({ name: "column", label: `State: ${COLUMN_TITLES[filters.column]}` });
  }
  return chips;
}
