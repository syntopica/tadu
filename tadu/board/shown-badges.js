// Which of a card's badges say something the list does not already say:
// none for an attribute the list is grouped by, whose headings name it, or
// narrowed to one value by a filter, whose chip names it. The board's
// columns are states, so it passes "state" as its grouping.
export function shownBadges(group, filters) {
  const one = (field) =>
    filters.rules.some((rule) => rule.field === field && rule.op === "any" && rule.values.length === 1);
  return {
    kind: group !== "kind" && !one("kind"),
    priority: group !== "priority" && !one("priority"),
  };
}
