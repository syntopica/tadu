// How many lines of each field a change added and removed, as `tadu
// changes` sums them up (Python's line_facts): `notes: 1 added, 1 removed`
// per field, in the order the fields first appear.
export function lineFacts(lines) {
  const counts = new Map();
  for (const line of lines) {
    const count = counts.get(line.field) ?? { "+": 0, "-": 0 };
    count[line.op] += 1;
    counts.set(line.field, count);
  }
  return [...counts].map(([field, count]) => {
    const parts = [["+", "added"], ["-", "removed"]]
      .filter(([op]) => count[op] > 0)
      .map(([op, word]) => `${count[op]} ${word}`);
    return `${field}: ${parts.join(", ")}`;
  });
}
