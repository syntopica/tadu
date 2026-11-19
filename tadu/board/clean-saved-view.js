import { cleanFilters } from "./clean-filters.js";
import { VIEW_TITLES } from "./view-titles.js";

// A saved view as stored, reduced to the known keys with values of the
// expected type (its filters as cleanFilters reads them); anything else
// falls back to its default. Its places are checked against the workspace
// when restored; a view saved with one place (`where`) brings it as a list
// of one, and one saved before scopes existed its project and repository
// filters as one place.
// Null when it has no usable name.
export function cleanSavedView(raw) {
  if (raw === null || typeof raw !== "object" || typeof raw.name !== "string") {
    return null;
  }
  const name = raw.name.trim().slice(0, 40);
  if (name === "") {
    return null;
  }
  const pick = (value, allowed, fallback) => (allowed.includes(value) ? value : fallback);
  const text = (value) => (typeof value === "string" ? value : "");
  const legacy = raw.where ?? { project: raw.filters?.project, repository: raw.filters?.repository };
  const given = Array.isArray(raw.places) ? raw.places : [legacy];
  const places = given.filter((place) => place !== null && typeof place === "object").map((place) => ({
    company: text(place?.company),
    project: text(place?.project),
    repository: text(place?.repository),
  }));
  return {
    name,
    view: pick(raw.view, VIEW_TITLES.map(([view]) => view), "board"),
    text: text(raw.text),
    filters: cleanFilters(raw.filters ?? null),
    places,
    scope: pick(raw.scope, ["all", "mine", "unassigned"], "all"),
    group: pick(
      raw.group,
      ["state", "company", "project", "repository", "priority", "kind", "assignee", "day"],
      "state",
    ),
    sort: pick(raw.sort, ["priority", "due", "title", "location", "closed"], "priority"),
  };
}
