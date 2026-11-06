import { cleanWhere } from "./clean-where.js";

// The scope a page starts in: the URL hash's when it names one, else the
// one this browser last used for the workspace.
export function initialWhere(hash, stored, index) {
  return cleanWhere(hash.given ? hash.where : stored, index);
}
