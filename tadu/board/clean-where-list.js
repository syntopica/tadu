import { cleanWhere } from "./clean-where.js";
import { sameWhere } from "./same-where.js";

// A stored list of scopes (recent or starred) kept to the valid, distinct,
// non-empty ones the current workspace still has.
export function cleanWhereList(raw, index) {
  const result = [];
  for (const entry of Array.isArray(raw) ? raw : []) {
    const where = cleanWhere(entry, index);
    const empty = where.company === "" && where.project === "" && where.repository === "";
    if (!empty && !result.some((old) => sameWhere(old, where))) {
      result.push(where);
    }
  }
  return result;
}
