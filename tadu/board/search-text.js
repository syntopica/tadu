// Everything a search may match in one card, lowercased once per load: its
// text, where it lives (keys and display names) and its fields.
export function searchText(card) {
  return [
    card.title,
    card.text,
    card.key,
    card.repository,
    card.path,
    card.project ?? "",
    card.place.company,
    card.place.project,
    ...card.organizations.map((entry) => `${entry.org} ${entry.role}`),
    ...card.place.relations.map((relation) => relation.name),
    ...card.assignees,
    ...card.labels,
  ]
    .join("\n")
    .toLowerCase();
}
