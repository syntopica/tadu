// "Client: Automate Texas": a project's relation to an organization.
export function relationLabel(relation) {
  return `${relation.role[0].toUpperCase()}${relation.role.slice(1)}: ${relation.name}`;
}
