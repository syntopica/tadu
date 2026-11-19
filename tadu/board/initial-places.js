import { cleanPlaces } from "./clean-places.js";

// The places a page starts in: the URL hash's when it names any, else the
// ones this browser last used for the workspace.
export function initialPlaces(hash, stored, index) {
  return cleanPlaces(hash.given ? hash.places : stored, index);
}
