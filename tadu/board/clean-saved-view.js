import { DEFAULT_FILTERS } from "./default-filters.js";

// A saved view as stored, reduced to the known keys with values of the
// expected type; anything else falls back to its default. Null when it has
// no usable name.
export function cleanSavedView(raw) {
  if (raw === null || typeof raw !== "object" || typeof raw.name !== "string") {
    return null;
  }
  const name = raw.name.trim().slice(0, 40);
  if (name === "") {
    return null;
  }
  const pick = (value, allowed, fallback) => (allowed.includes(value) ? value : fallback);
  const filters = {};
  for (const [key, fallback] of Object.entries(DEFAULT_FILTERS)) {
    const value = raw.filters?.[key];
    filters[key] = typeof value === typeof fallback ? value : fallback;
  }
  return {
    name,
    view: pick(raw.view, ["mine", "all", "blocked", "portfolio", "done", "board"], "board"),
    text: typeof raw.text === "string" ? raw.text : "",
    filters,
    scope: pick(raw.scope, ["all", "mine", "unassigned"], "all"),
    group: pick(
      raw.group,
      ["state", "project", "repository", "priority", "assignee", "day"],
      "state",
    ),
    sort: pick(raw.sort, ["priority", "due", "title", "location", "closed"], "priority"),
  };
}
