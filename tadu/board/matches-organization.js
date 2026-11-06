// An organization and a role chosen together must hold for the same
// {role, org} pair, as `tadu list --org --role` does.
export function matchesOrganization(card, organization, role) {
  if (organization === "" && role === "") {
    return true;
  }
  return card.organizations.some(
    (entry) =>
      (organization === "" || entry.org === organization) && (role === "" || entry.role === role),
  );
}
