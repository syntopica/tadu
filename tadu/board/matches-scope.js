// The Blocked view's sub-chips: all, blocked for me, unassigned.
export function matchesScope(card, scope, me) {
  if (scope === "mine") {
    return me !== null && card.assignees.includes(me);
  }
  if (scope === "unassigned") {
    return card.assignees.length === 0;
  }
  return true;
}
