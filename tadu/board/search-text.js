// Everything a search may match in one card, lowercased once per load.
export function searchText(card) {
  return [
    card.title,
    card.text,
    card.key,
    card.repository,
    card.path,
    card.project ?? "",
    ...card.organizations.map((entry) => `${entry.org} ${entry.role}`),
    ...card.assignees,
    ...card.labels,
  ]
    .join("\n")
    .toLowerCase();
}
