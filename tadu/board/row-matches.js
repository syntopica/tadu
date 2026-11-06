import { matchesQuery } from "./matches-query.js";

// A portfolio row matches a search by its name or any repository it covers.
export function rowMatches(row, query) {
  const names = [row.label, ...row.repositories].join("\n").toLowerCase();
  return matchesQuery(names, query);
}
