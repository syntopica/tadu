// Whether two scopes choose the same company, project and repository.
export function sameWhere(a, b) {
  return a.company === b.company && a.project === b.project && a.repository === b.repository;
}
