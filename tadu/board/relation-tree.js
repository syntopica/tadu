import { cleanWhere } from "./clean-where.js";
import { compareRows } from "./compare-rows.js";
import { projectNode } from "./project-node.js";
import { repositoryBuckets } from "./repository-buckets.js";
import { sumBuckets } from "./sum-buckets.js";

// The portfolio's relations view for one role such as "client": each
// organization holding that role over projects in scope, with those
// projects under it, then the projects with no such relation. This is not
// ownership: a project may sit under several organizations here.
export function relationTree(cards, index, where, role, keepEmpty) {
  const byRepository = repositoryBuckets(cards);
  const shown = (row) => keepEmpty || row.buckets.total > 0;
  const groups = new Map();
  for (const project of index.projects.values()) {
    const owner = cleanWhere({ company: where.company, project: project.key }, index).company;
    const outside =
      (where.company !== "" && owner !== where.company) ||
      (where.project !== "" && project.key !== where.project);
    if (outside) {
      continue;
    }
    const node = projectNode(project, owner, byRepository, where);
    if (!shown(node) || node.children.length === 0) {
      continue;
    }
    const orgs = project.relations.filter((relation) => relation.role === role);
    for (const { org, name } of orgs.length > 0 ? orgs : [{ org: "", name: `No ${role}` }]) {
      if (!groups.has(org)) {
        groups.set(org, {
          kind: "organization",
          key: `o:${org}`,
          label: name,
          role,
          filter: org === "" ? null : { organization: org, role },
          children: [],
          last: org === "",
        });
      }
      groups.get(org).children.push(node);
    }
  }
  return [...groups.values()]
    .map((group) => ({
      ...group,
      relations: [],
      buckets: sumBuckets(group.children),
      target: null,
      children: group.children.sort(compareRows),
      projects: group.children.length,
      repositories: group.children.reduce((sum, child) => sum + child.children.length, 0),
    }))
    .sort(compareRows);
}
