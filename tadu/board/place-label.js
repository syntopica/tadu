// "Pixel Potion › VerticaGTM": a card's company and project by display
// name, whichever it has; "" for a repository in no project.
export function placeLabel(card) {
  return [card.place.company, card.place.project].filter((name) => name !== "").join(" › ");
}
