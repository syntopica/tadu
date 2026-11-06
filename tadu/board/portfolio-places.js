import { rolesByOrg } from "./roles-by-org.js";

// Where one card is counted in the portfolio: a list of {group, child}
// pairs, empty when the role filter excludes it. A card counts once under
// each of its project's organizations, whatever roles the organization has.
// Each row's `filter` opens the list of exactly the cards it counts.
export function portfolioPlaces(card, groupBy, role) {
  const orgs = rolesByOrg(card.organizations, role);
  if (role !== "" && orgs.length === 0) {
    return [];
  }
  const withRole = role === "" ? {} : { role };
  const repository = { key: `r:${card.repository}`, label: card.repository, roles: [] };
  if (card.project === null) {
    const group = { key: "none", label: "No project", roles: [], filter: null, last: true };
    return [{ group, child: { ...repository, filter: { repository: card.repository } } }];
  }
  const project = { key: `p:${card.project}`, label: card.project };
  if (groupBy === "project") {
    const roles = orgs.flatMap((entry) => entry.roles.map((name) => `${entry.org} · ${name}`));
    const group = {
      ...project,
      roles,
      filter: { project: card.project, ...withRole },
      last: false,
    };
    const filter = { project: card.project, repository: card.repository, ...withRole };
    return [{ group, child: { ...repository, filter } }];
  }
  if (orgs.length === 0) {
    const group = { key: "o:", label: "No organization", roles: [], filter: null, last: true };
    return [{ group, child: { ...project, roles: [], filter: { project: card.project } } }];
  }
  return orgs.map(({ org, roles }) => ({
    group: {
      key: `o:${org}`,
      label: org,
      roles,
      filter: { organization: org, ...withRole },
      last: false,
    },
    child: { ...project, roles, filter: { organization: org, project: card.project, ...withRole } },
  }));
}
