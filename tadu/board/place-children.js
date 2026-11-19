import { cleanWhere } from "./clean-where.js";

// The places one level inside `place`: a company's projects, a project's
// repositories, nothing inside a repository; the whole workspace holds
// the companies, or the repositories when there are none.
export function placeChildren(place, index) {
  if (place.repository !== "") {
    return [];
  }
  if (place.project !== "") {
    const keys = index.projects.get(place.project)?.repositories ?? [];
    return keys.map((key) => ({ ...place, repository: key }));
  }
  if (place.company !== "") {
    const keys = index.companies.find((entry) => entry.id === place.company)?.projects ?? [];
    return keys.map((key) => ({ company: place.company, project: key, repository: "" }));
  }
  if (index.companies.length > 0) {
    return index.companies.map((entry) => ({ company: entry.id, project: "", repository: "" }));
  }
  return [...index.repositories.keys()].map((key) => cleanWhere({ repository: key }, index));
}
