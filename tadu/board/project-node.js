import { compareRows } from "./compare-rows.js";
import { emptyBuckets } from "./empty-buckets.js";
import { NO_PLACE } from "./no-place.js";
import { sumBuckets } from "./sum-buckets.js";

// A portfolio project row with one child row per repository in scope (all
// of them, or only `where.repository`), each with its counts and the scope a
// click opens. `company` is the company row it sits under ("" for none).
export function projectNode(project, company, byRepository, where) {
  const children = project.repositories
    .filter((key) => where.repository === "" || key === where.repository)
    .map((key) => ({
      kind: "repository",
      key: `r:${key}`,
      label: key,
      relations: [],
      buckets: byRepository.get(key) ?? emptyBuckets(),
      target: { company, project: project.key, repository: key },
      children: [],
      last: false,
    }))
    .sort(compareRows);
  return {
    kind: "project",
    key: `p:${company}:${project.key}`,
    label: project.name,
    relations: project.relations,
    buckets: sumBuckets(children),
    target: { company, project: project.key, repository: "" },
    children,
    last: project.key === NO_PLACE,
  };
}
