import { el } from "./el.js";
import { icon } from "./icon.js";
import { relationLabel } from "./relation-label.js";

// A badge naming a project's relation, "Client: Automate Texas"; a
// relation, never ownership.
export function relationBadge(relation) {
  const badge = el("span", "relation");
  badge.append(icon("users"), el("span", "", relationLabel(relation)));
  return badge;
}
