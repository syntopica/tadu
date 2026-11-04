// tadu board: which cards the current filter choice shows. Pure: it reads
// only its arguments, so tests run it outside a browser.
"use strict";

// The values a card offers to each single-value filter select.
const FILTER_VALUES = {
  repository: (card) => [card.repository],
  project: (card) => (card.project === null ? [] : [card.project]),
  organization: (card) => card.organizations.map((entry) => entry.org),
  role: (card) => card.organizations.map((entry) => entry.role),
  assignee: (card) => card.assignees,
  priority: (card) => (card.priority === null ? [] : [card.priority]),
  label: (card) => card.labels,
};
const SINGLE_FILTERS = ["repository", "project", "assignee", "priority", "label"];

// An organization and a role chosen together must hold for the same
// {role, org} pair, as `tadu list --org --role` does.
function matchesOrganization(card, organization, role) {
  if (organization === "" && role === "") {
    return true;
  }
  return card.organizations.some(
    (entry) =>
      (organization === "" || entry.org === organization) && (role === "" || entry.role === role),
  );
}

// `choice` holds each filter's selected value ("" for any), plus waitingOnMe,
// showCancelled and me (the local person, or null).
function cardVisible(card, choice) {
  if (card.column === "cancelled" && !choice.showCancelled) {
    return false;
  }
  for (const name of SINGLE_FILTERS) {
    if (choice[name] !== "" && !FILTER_VALUES[name](card).includes(choice[name])) {
      return false;
    }
  }
  if (!matchesOrganization(card, choice.organization, choice.role)) {
    return false;
  }
  if (choice.waitingOnMe) {
    return card.column === "blocked" && choice.me !== null && card.assignees.includes(choice.me);
  }
  return true;
}
