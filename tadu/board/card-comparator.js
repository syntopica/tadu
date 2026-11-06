import { compareClosed } from "./compare-closed.js";
import { compareDue } from "./compare-due.js";
import { compareLocation } from "./compare-location.js";
import { comparePriority } from "./compare-priority.js";
import { compareTitle } from "./compare-title.js";

// The comparison for a sort name; unknown names sort by priority.
export function cardComparator(sort) {
  const orders = {
    priority: [comparePriority, compareDue, compareLocation],
    due: [compareDue, comparePriority, compareLocation],
    title: [compareTitle, compareLocation],
    location: [compareLocation],
    closed: [compareClosed, compareLocation],
  };
  const steps = orders[sort] ?? orders.priority;
  return (a, b) => {
    for (const step of steps) {
      const result = step(a, b);
      if (result !== 0) {
        return result;
      }
    }
    return 0;
  };
}
