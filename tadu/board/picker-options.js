import { cleanWhere } from "./clean-where.js";
import { EMPTY_WHERE } from "./empty-where.js";
import { matchesQuery } from "./matches-query.js";
import { NO_PLACE } from "./no-place.js";
import { plural } from "./plural.js";
import { whereParts } from "./where-parts.js";

// The choices of a scope picker, each {group, label, detail, target}, where
// `target` is the whole scope choosing it sets. `kind` is "company",
// "project", "repository" or "switcher" (every level, plus the starred and
// recent scopes while nothing is typed). Projects narrow to the chosen
// company and repositories to the chosen project; picking a project sets its
// company and a repository its project. `lists` holds {favourites, recent}.
export function pickerOptions(kind, index, where, text, lists) {
  const typed = text.trim();
  const keep = (option) =>
    typed === "" || matchesQuery(`${option.label}\n${option.detail}`.toLowerCase(), typed);
  const label = (target) =>
    whereParts(target, index)
      .map((part) => part.label)
      .join(" › ");
  const companies = () =>
    index.companies.map((company) => ({
      group: "Companies",
      label: company.name,
      detail: plural(company.projects.filter((key) => key !== NO_PLACE).length, "project"),
      target: { company: company.id, project: "", repository: "" },
    }));
  const projects = (company) =>
    (company === ""
      ? [...index.projects.keys()]
      : (index.companies.find((entry) => entry.id === company)?.projects ?? []))
      .map((key) => cleanWhere({ company, project: key }, index))
      .filter((target) => company === "" || target.company === company)
      .map((target) => ({
        group: "Projects",
        label: index.projects.get(target.project).name,
        detail: company === "" ? whereParts(target, index)[0].label : "",
        target,
      }));
  const repositories = (scope) =>
    [...index.repositories.keys()]
      .map((key) => cleanWhere({ ...scope, repository: key }, index))
      .filter(
        (target) =>
          (scope.company === "" || target.company === scope.company) &&
          (scope.project === "" || target.project === scope.project),
      )
      .map((target) => ({
        group: "Repositories",
        label: target.repository,
        detail: index.projects.get(target.project)?.name ?? "",
        target,
      }));
  const all = (name, target) => ({ group: "", label: name, detail: "", target });
  if (kind === "company") {
    return [all("All companies", EMPTY_WHERE), ...companies()].filter(keep);
  }
  if (kind === "project") {
    const inside = { ...EMPTY_WHERE, company: where.company };
    return [all("All projects", inside), ...projects(where.company)].filter(keep);
  }
  if (kind === "repository") {
    const inside = { ...where, repository: "" };
    return [all("All repositories", inside), ...repositories(inside)].filter(keep);
  }
  const saved = (group, list) =>
    list.map((target) => ({ group, label: label(target), detail: "", target }));
  if (typed === "") {
    return [
      all("All companies", EMPTY_WHERE),
      ...saved("Starred", lists.favourites),
      ...saved("Recent", lists.recent),
      ...companies(),
    ];
  }
  return [...companies(), ...projects(""), ...repositories(EMPTY_WHERE)].filter(keep);
}
