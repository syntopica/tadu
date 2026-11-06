import { matchesQuery } from "./matches-query.js";

// Keep the groups whose name matches, whole, and in the others only the
// matching children.
export function filterTree(tree, query) {
  if (query.trim() === "") {
    return tree;
  }
  const result = [];
  for (const row of tree) {
    if (matchesQuery(row.label.toLowerCase(), query)) {
      result.push(row);
      continue;
    }
    const children = row.children.filter((child) => matchesQuery(child.label.toLowerCase(), query));
    if (children.length > 0) {
      result.push({ ...row, children });
    }
  }
  return result;
}
