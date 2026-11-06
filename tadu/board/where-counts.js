import { NO_PLACE } from "./no-place.js";
import { plural } from "./plural.js";

// What a scope holds, before its item count: "13 companies · 66 projects ·
// 96 repositories" for the workspace, "12 projects" for a company,
// "4 repositories" for a project, nothing for one repository.
export function whereCounts(where, index) {
  if (where.repository !== "") {
    return [];
  }
  if (where.project !== "") {
    return [plural(index.projects.get(where.project)?.repositories.length ?? 0, "repository")];
  }
  if (where.company !== "") {
    const company = index.companies.find((entry) => entry.id === where.company);
    const keys = (company?.projects ?? []).filter((key) => key !== NO_PLACE);
    return [plural(keys.length, "project")];
  }
  const companies = index.companies.filter((entry) => entry.id !== NO_PLACE).length;
  const projects = [...index.projects.keys()].filter((key) => key !== NO_PLACE).length;
  return [
    ...(companies > 0 ? [plural(companies, "company")] : []),
    ...(projects > 0 ? [plural(projects, "project")] : []),
    plural(index.repositories.size, "repository"),
  ];
}
