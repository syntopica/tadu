import { sameWhere } from "./same-where.js";

// The recent scopes with `where` first, without repeats, at most five; the
// whole workspace is not recorded.
export function pushRecent(recent, where) {
  if (where.company === "" && where.project === "" && where.repository === "") {
    return recent;
  }
  const { company, project, repository } = where;
  return [{ company, project, repository }, ...recent.filter((old) => !sameWhere(old, where))].slice(0, 5);
}
