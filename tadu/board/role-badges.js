import { el } from "./el.js";

// Small badges naming roles such as client or agency.
export function roleBadges(roles) {
  return roles.map((role) => el("span", "role", role));
}
