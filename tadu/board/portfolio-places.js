// Where one card is counted in the portfolio: a list of {group, child}
// pairs, empty when the role filter excludes it. A card of a project with
// two organizations counts once under each organization.
export function portfolioPlaces(card, groupBy, role) {
  const entries = card.organizations.filter((entry) => role === "" || entry.role === role);
  if (role !== "" && entries.length === 0) {
    return [];
  }
  const repository = { key: `r:${card.repository}`, label: card.repository, roles: [] };
  if (card.project === null) {
    const group = { key: "none", label: "No project", roles: [], filter: null, last: true };
    return [{ group, child: { ...repository, filter: { repository: card.repository } } }];
  }
  const project = {
    key: `p:${card.project}`,
    label: card.project,
    filter: { project: card.project },
  };
  if (groupBy === "project") {
    const roles = entries.map((entry) => `${entry.org} · ${entry.role}`);
    const filter = { project: card.project, repository: card.repository };
    return [{ group: { ...project, roles, last: false }, child: { ...repository, filter } }];
  }
  if (entries.length === 0) {
    const group = { key: "o:", label: "No organization", roles: [], filter: null, last: true };
    return [{ group, child: { ...project, roles: [] } }];
  }
  return entries.map((entry) => ({
    group: {
      key: `o:${entry.org}`,
      label: entry.org,
      roles: [entry.role],
      filter: { organization: entry.org },
      last: false,
    },
    child: { ...project, roles: [entry.role] },
  }));
}
