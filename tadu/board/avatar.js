import { el } from "./el.js";
import { initials } from "./initials.js";

// A round badge with a person's initials; the full ID is its tooltip.
export function avatar(person) {
  const node = el("span", "avatar", initials(person));
  node.title = person;
  return node;
}
