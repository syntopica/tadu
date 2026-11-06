import { NO_PLACE } from "./no-place.js";

// A scope from a URL, storage or a saved view made valid for the current
// workspace: unknown values are dropped, a repository brings its project
// and a project its company, so the three levels always agree.
export function cleanWhere(raw, index) {
  const text = (value) => (typeof value === "string" ? value : "");
  let company = text(raw?.company);
  let project = text(raw?.project);
  let repository = text(raw?.repository);
  if (!index.repositories.has(repository)) {
    repository = "";
  }
  if (!index.projects.has(project)) {
    project = "";
  }
  if (!index.companies.some((entry) => entry.id === company)) {
    company = "";
  }
  if (repository !== "") {
    const owner = index.repositories.get(repository).project;
    project = owner ?? (index.projects.has(NO_PLACE) ? NO_PLACE : "");
  }
  if (project !== "") {
    const owners = index.projects.get(project).companies;
    if (!owners.includes(company)) {
      company = owners[0] ?? NO_PLACE;
    }
  }
  return { company, project, repository };
}
