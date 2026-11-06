import { compareRows } from "./compare-rows.js";
import { NO_PLACE } from "./no-place.js";
import { projectNode } from "./project-node.js";
import { repositoryBuckets } from "./repository-buckets.js";
import { sumBuckets } from "./sum-buckets.js";

// The portfolio's ownership tree inside a scope: Company > Project >
// Repository. Each project sits under the companies that own it, never
// under a client, and every row sums distinct repositories, so no card is
// counted twice within a company. Without projects the rows are the
// repositories themselves. `keepEmpty` keeps rows that count nothing.
export function companyTree(cards, index, where, keepEmpty) {
  const byRepository = repositoryBuckets(cards);
  const shown = (row) => keepEmpty || row.buckets.total > 0;
  if (index.projects.size === 0) {
    const project = { key: "", name: "", relations: [], repositories: [...index.repositories.keys()] };
    return projectNode(project, "", byRepository, where).children.filter(shown);
  }
  return index.companies
    .filter((company) => where.company === "" || company.id === where.company)
    .map((company) => {
      const children = company.projects
        .filter((key) => where.project === "" || key === where.project)
        .map((key) => projectNode(index.projects.get(key), company.id, byRepository, where))
        .filter(shown)
        .sort(compareRows);
      return {
        kind: "company",
        key: `c:${company.id}`,
        label: company.name,
        relations: [],
        buckets: sumBuckets(children),
        target: { company: company.id, project: "", repository: "" },
        children,
        projects: children.filter((child) => child.target.project !== NO_PLACE).length,
        repositories: children.reduce((sum, child) => sum + child.children.length, 0),
        last: company.id === NO_PLACE,
      };
    })
    .filter((row) => row.children.length > 0 && shown(row))
    .sort(compareRows);
}
