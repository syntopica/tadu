import { locationLabel } from "./location-label.js";

// Where an item lives, short enough for a list row or a board card: a
// TODO.md item's "TODO.md:61-69", a task's id as commands print it
// ("t-55161023"), since its file is named by the id and holds nothing else.
export function rowLocation(card) {
  return card.path.endsWith(".json") ? card.key.slice(0, 10) : locationLabel(card);
}
