// Count one card into portfolio counts; Ready counts as backlog and
// cancelled work is not counted.
export function addToBuckets(buckets, card) {
  const bucket = card.column === "ready" ? "backlog" : card.column;
  if (!(bucket in buckets) || bucket === "total") {
    return;
  }
  buckets[bucket] += 1;
  buckets.total += 1;
}
