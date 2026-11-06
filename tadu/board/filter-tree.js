import { matchesQuery } from "./matches-query.js";
import { rowMatches } from "./row-matches.js";

// Keep the groups whose name matches, whole, and in the others only the
// children whose name or repositories match.
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
    const children = row.children.filter((child) => rowMatches(child, query));
    if (children.length > 0) {
      result.push({ ...row, children });
    }
  }
  return result;
}
