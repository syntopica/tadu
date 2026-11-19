import { cleanWhere } from "./clean-where.js";
import { EMPTY_WHERE } from "./empty-where.js";
import { NO_PLACE } from "./no-place.js";
import { placeCovers } from "./place-covers.js";
import { plural } from "./plural.js";
import { whereCounts } from "./where-counts.js";

// What the chosen places hold, before the item count: as whereCounts says
// it for none or one place; for several, the projects and repositories
// they hold together ("2 projects · 3 repositories").
export function placesCounts(places, index) {
  if (places.length <= 1) {
    return whereCounts(places[0] ?? EMPTY_WHERE, index);
  }
  const repositories = [...index.repositories.keys()]
    .map((key) => cleanWhere({ repository: key }, index))
    .filter((repository) => places.some((place) => placeCovers(place, repository, index)));
  const projects = new Set(repositories.map((repository) => repository.project).filter((key) => key !== "" && key !== NO_PLACE));
  return [
    ...(projects.size > 0 ? [plural(projects.size, "project")] : []),
    plural(repositories.length, "repository"),
  ];
}
