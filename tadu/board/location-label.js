// "TODO.md:275-288", or "TODO.md:61" for a one-line item.
export function locationLabel(card) {
  const span = card.end_line > card.line ? `${card.line}-${card.end_line}` : `${card.line}`;
  return `${card.path}:${span}`;
}
