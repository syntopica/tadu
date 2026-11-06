import { COLUMN_TITLES } from "./column-titles.js";
import { PRIORITY_TITLES } from "./priority-titles.js";

// The active filters as removable chips: {name, label}; organizations by
// display name (`orgNames`). The scope has chips of its own.
export function activeChips(filters, orgNames) {
  const names = {
    organization: "Organization",
    role: "Role",
    assignee: "Assignee",
    priority: "Priority",
    label: "Label",
    dueBefore: "Due before",
  };
  const shown = {
    priority: (value) => PRIORITY_TITLES[value],
    organization: (value) => orgNames.get(value) ?? value,
  };
  const chips = [];
  for (const [name, title] of Object.entries(names)) {
    if (filters[name] !== "") {
      const value = shown[name]?.(filters[name]) ?? filters[name];
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
