// Whether `outer` holds all of `inner`: the same repository, or its
// project, or a company that owns its project (a project may have several
// companies), or the whole workspace. A company holds what it will own
// later too, since it is matched by company, not by a list.
export function placeCovers(outer, inner, index) {
  if (outer.repository !== "") {
    return inner.repository === outer.repository;
  }
  if (outer.project !== "") {
    return inner.project === outer.project;
  }
  if (outer.company === "") {
    return true;
  }
  const owners = index.projects.get(inner.project)?.companies ?? [];
  return inner.company === outer.company || owners.includes(outer.company);
}
