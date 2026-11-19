import { capitalize } from "./capitalize.js";

// "Client: Automate Texas": a project's relation to an organization.
export function relationLabel(relation) {
  return `${capitalize(relation.role)}: ${relation.name}`;
}
