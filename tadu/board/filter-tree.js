import { matchesQuery } from "./matches-query.js";

// Keep the rows whose name matches, whole, and in the others only the
// children that match at some depth.
export function filterTree(rows, query) {
  if (query.trim() === "") {
    return rows;
  }
  const result = [];
  for (const row of rows) {
    if (matchesQuery(row.label.toLowerCase(), query)) {
      result.push(row);
      continue;
    }
    const children = filterTree(row.children, query);
    if (children.length > 0) {
      result.push({ ...row, children });
    }
  }
  return result;
}
