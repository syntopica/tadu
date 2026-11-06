// The stable ID shortened for display, "t-55161023…"; null without an ID.
export function shortId(card) {
  return card.stable ? `${card.key.slice(0, 10)}…` : null;
}
