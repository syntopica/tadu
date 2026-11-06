// Summary chips in reading order: board order on a desktop; on a phone what
// needs attention first, Blocked, In progress, then the rest.
export function summaryOrder(columns, phone) {
  if (!phone) {
    return columns;
  }
  const first = ["blocked", "in_progress", "backlog"].filter((column) => columns.includes(column));
  return [...first, ...columns.filter((column) => !first.includes(column))];
}
