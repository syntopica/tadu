import { emptyBuckets } from "./empty-buckets.js";

// The counts of several rows added together.
export function sumBuckets(rows) {
  const total = emptyBuckets();
  for (const row of rows) {
    for (const key of Object.keys(total)) {
      total[key] += row.buckets[key];
    }
  }
  return total;
}
