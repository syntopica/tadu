// Groups flattened into list rows; a collapsed group keeps only its header.
export function listRows(groups, collapsed) {
  const rows = [];
  for (const group of groups) {
    const closed = collapsed.has(group.key);
    rows.push({ kind: "group", key: group.key, label: group.label, count: group.cards.length, closed });
    if (!closed) {
      for (const card of group.cards) {
        rows.push({ kind: "card", card });
      }
    }
  }
  return rows;
}
