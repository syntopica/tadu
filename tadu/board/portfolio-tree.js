import { addToBuckets } from "./add-to-buckets.js";
import { compareRows } from "./compare-rows.js";
import { emptyBuckets } from "./empty-buckets.js";
import { mergeRoles } from "./merge-roles.js";
import { portfolioPlaces } from "./portfolio-places.js";

// Group rows (organizations or projects) with nested child rows, each with
// its counts and the repositories it covers, sorted by total. `groupBy` is
// "organization" or "project".
export function portfolioTree(cards, groupBy, role) {
  const groups = new Map();
  for (const card of cards) {
    for (const { group, child } of portfolioPlaces(card, groupBy, role)) {
      if (!groups.has(group.key)) {
        groups.set(group.key, {
          ...group,
          roles: [],
          repositories: new Set(),
          buckets: emptyBuckets(),
          children: new Map(),
        });
      }
      const row = groups.get(group.key);
      mergeRoles(row.roles, group.roles);
      row.repositories.add(card.repository);
      addToBuckets(row.buckets, card);
      if (!row.children.has(child.key)) {
        row.children.set(child.key, {
          ...child,
          roles: [],
          repositories: new Set(),
          buckets: emptyBuckets(),
          last: false,
        });
      }
      const leaf = row.children.get(child.key);
      mergeRoles(leaf.roles, child.roles);
      leaf.repositories.add(card.repository);
      addToBuckets(leaf.buckets, card);
    }
  }
  return [...groups.values()]
    .map((row) => ({ ...row, children: [...row.children.values()].sort(compareRows) }))
    .sort(compareRows);
}
