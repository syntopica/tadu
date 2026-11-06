// The URL hash that reopens a scope and view; levels left at "all" are omitted.
export function hashText(where, view) {
  const params = new URLSearchParams();
  for (const level of ["company", "project", "repository"]) {
    if (where[level] !== "") {
      params.set(level, where[level]);
    }
  }
  params.set("view", view);
  return `#${params}`;
}
