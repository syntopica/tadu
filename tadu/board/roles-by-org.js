// A card's organization entries merged per organization: [{org, roles}],
// keeping only entries whose role passes `role` ("" for any).
export function rolesByOrg(organizations, role) {
  const byOrg = new Map();
  for (const entry of organizations) {
    if (role !== "" && entry.role !== role) {
      continue;
    }
    if (!byOrg.has(entry.org)) {
      byOrg.set(entry.org, []);
    }
    if (!byOrg.get(entry.org).includes(entry.role)) {
      byOrg.get(entry.org).push(entry.role);
    }
  }
  return [...byOrg].map(([org, roles]) => ({ org, roles }));
}
