// A place's identity by its narrowest level: "r:shop" for a repository,
// "p:storefront" for a project (whichever company it sits under),
// "c:acme" for a company, "" for the whole workspace.
export function placeKey(place) {
  if (place.repository !== "") {
    return `r:${place.repository}`;
  }
  if (place.project !== "") {
    return `p:${place.project}`;
  }
  return place.company === "" ? "" : `c:${place.company}`;
}
