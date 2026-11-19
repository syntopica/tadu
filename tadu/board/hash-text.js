import { placeKey } from "./place-key.js";

// The URL hash that reopens the chosen places and the view: one `place`
// per place, by its narrowest level ("repository:shop").
export function hashText(places, view) {
  const params = new URLSearchParams();
  const levels = { c: "company", p: "project", r: "repository" };
  for (const place of places) {
    const [level, ...key] = placeKey(place).split(":");
    params.append("place", `${levels[level]}:${key.join(":")}`);
  }
  params.set("view", view);
  return `#${params}`;
}
