import { compareOpen } from "./compare-open.js";
import { NO_PLACE } from "./no-place.js";
import { openCounts } from "./open-counts.js";

// The payload's workspace structure indexed once per load. A project's
// companies are the organizations it lists under the role "company"; its
// other roles are relations. Projects naming no company, and a "No project"
// entry for repositories in no project, sit under a "No company" entry.
// Without projects (a repositories-only workspace) there are no companies.
export function workspaceIndex(workspace, cards) {
  const orgNames = new Map(workspace.organizations.map((org) => [org.id, org.name]));
  const open = openCounts(cards);
  const repositories = new Map(
    workspace.repositories.map((repo) => [
      repo.key,
      { key: repo.key, name: repo.key, project: null, open: open.get(repo.key) ?? 0 },
    ]),
  );
  const projects = new Map();
  const roles = new Set();
  for (const raw of workspace.projects) {
    const companies = raw.roles.filter((r) => r.role === "company").map((r) => r.org);
    const relations = raw.roles
      .filter((r) => r.role !== "company")
      .map((r) => ({ role: r.role, org: r.org, name: orgNames.get(r.org) ?? r.org }));
    relations.forEach((r) => roles.add(r.role));
    const members = raw.repositories.filter((key) => repositories.has(key));
    members.forEach((key) => {
      repositories.get(key).project = raw.key;
    });
    const total = members.reduce((sum, key) => sum + repositories.get(key).open, 0);
    projects.set(raw.key, { ...raw, companies, relations, repositories: members, open: total });
  }
  const orphans = [...repositories.values()].filter((repo) => repo.project === null);
  if (projects.size > 0 && orphans.length > 0) {
    const total = orphans.reduce((sum, repo) => sum + repo.open, 0);
    const keys = orphans.map((repo) => repo.key);
    projects.set(NO_PLACE, {
      key: NO_PLACE,
      name: "No project",
      companies: [],
      relations: [],
      repositories: keys,
      open: total,
    });
  }
  const companies = new Map();
  for (const project of projects.values()) {
    const owners = project.companies.length > 0 ? project.companies : [NO_PLACE];
    for (const id of owners) {
      if (!companies.has(id)) {
        const name = id === NO_PLACE ? "No company" : (orgNames.get(id) ?? id);
        companies.set(id, { id, name, projects: [], open: 0 });
      }
      companies.get(id).projects.push(project);
      companies.get(id).open += project.open;
    }
  }
  const ordered = [...companies.values()]
    .map((company) => ({ ...company, projects: company.projects.sort(compareOpen) }))
    .sort((a, b) => (a.id === NO_PLACE) - (b.id === NO_PLACE) || compareOpen(a, b))
    .map((company) => ({ ...company, projects: company.projects.map((p) => p.key) }));
  return {
    orgNames,
    companies: ordered,
    projects,
    repositories,
    roles: [...roles].sort(),
  };
}
