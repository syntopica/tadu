// Where a card belongs, by display name: its project's companies (ids and
// names), the project's name and its relations such as a client. A card
// whose project the index does not know keeps the project key as its name.
export function cardPlace(card, index) {
  const project = card.project === null ? undefined : index.projects.get(card.project);
  const companies = project?.companies ?? [];
  return {
    companies,
    company: companies.map((id) => index.orgNames.get(id) ?? id).join(", "),
    project: project?.name ?? card.project ?? "",
    relations: (project?.relations ?? []).map(({ role, name }) => ({ role, name })),
  };
}
