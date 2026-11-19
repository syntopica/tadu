// Whether the page may change items of `repository`: the server lists the
// repositories both its --allow and the workspace's `access` let it change.
export function canChange(payload, repository) {
  return (payload?.writable ?? []).includes(repository);
}
