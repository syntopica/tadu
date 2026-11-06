// The cards the portfolio counts: not cancelled, in the state filter (Ready
// counts as Backlog), the top bar's project and the role filter.
export function portfolioCards(cards, portfolio, project) {
  const { state, role } = portfolio;
  return cards.filter(
    (card) =>
      card.column !== "cancelled" &&
      (state === "" || card.column === state || (state === "backlog" && card.column === "ready")) &&
      (project === "" || card.project === project) &&
      (role === "" || card.organizations.some((entry) => entry.role === role)),
  );
}
