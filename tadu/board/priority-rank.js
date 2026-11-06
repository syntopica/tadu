// Sort rank of a priority: urgent first, no priority last.
export function priorityRank(priority) {
  return { urgent: 0, high: 1, normal: 2, low: 3 }[priority] ?? 4;
}
