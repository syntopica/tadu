import { addToBuckets } from "./add-to-buckets.js";
import { emptyBuckets } from "./empty-buckets.js";

// Portfolio counts per repository key; each card counts once, in its own
// repository, so sums over distinct repositories never count a card twice.
export function repositoryBuckets(cards) {
  const byRepository = new Map();
  for (const card of cards) {
    if (!byRepository.has(card.repository)) {
      byRepository.set(card.repository, emptyBuckets());
    }
    addToBuckets(byRepository.get(card.repository), card);
  }
  return byRepository;
}
