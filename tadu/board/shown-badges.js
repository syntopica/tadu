// Which of a card's badges say something the list does not already say:
// none for an attribute the list is grouped by, whose headings name it, or
// narrowed to one value by a filter, whose chip names it. The board's
// columns are states, so it passes "state" as its grouping.
export function shownBadges(group, filters) {
  return {
    kind: group !== "kind" && filters.kind === "",
    priority: group !== "priority" && filters.priority === "",
  };
}
