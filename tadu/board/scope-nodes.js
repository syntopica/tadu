import { cleanWhere } from "./clean-where.js";

// The scope tree: companies (with No company last), their projects, then
// their repositories, each {key, kind, label, place, open, children}
// where `key` is unique in the tree (a project under two companies shows
// under each) and `open` its count of open items. Without companies the
// tree is the repositories alone.
export function scopeNodes(index) {
  const repository = (key, project) => ({
    key: `${project}/r:${key}`,
    kind: "repository",
    label: key,
    place: cleanWhere({ repository: key }, index),
    open: index.repositories.get(key).open,
    children: [],
  });
  if (index.companies.length === 0) {
    return [...index.repositories.keys()].map((key) => repository(key, ""));
  }
  return index.companies.map((company) => ({
    key: `c:${company.id}`,
    kind: "company",
    label: company.name,
    place: { company: company.id, project: "", repository: "" },
    open: company.open,
    children: company.projects.map((key) => {
      const project = index.projects.get(key);
      return {
        key: `c:${company.id}/p:${key}`,
        kind: "project",
        label: project.name,
        place: { company: company.id, project: key, repository: "" },
        open: project.open,
        children: project.repositories.map((name) => repository(name, `c:${company.id}/p:${key}`)),
      };
    }),
  }));
}
