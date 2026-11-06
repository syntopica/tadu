import { sameWhere } from "./same-where.js";

// The starred scopes with `where` added, or removed when already starred.
export function toggleFavourite(favourites, where) {
  if (favourites.some((old) => sameWhere(old, where))) {
    return favourites.filter((old) => !sameWhere(old, where));
  }
  const { company, project, repository } = where;
  return [...favourites, { company, project, repository }];
}
