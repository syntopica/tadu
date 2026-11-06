import { priorityRank } from "./priority-rank.js";

// Urgent first, no priority last.
export function comparePriority(a, b) {
  return priorityRank(a.priority) - priorityRank(b.priority);
}
