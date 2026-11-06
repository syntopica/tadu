import { addToBuckets } from "./add-to-buckets.js";
import { emptyBuckets } from "./empty-buckets.js";

// Portfolio stat cards: the counts of every card given, each counted once.
export function treeTotals(cards) {
  const buckets = emptyBuckets();
  for (const card of cards) {
    addToBuckets(buckets, card);
  }
  return buckets;
}
