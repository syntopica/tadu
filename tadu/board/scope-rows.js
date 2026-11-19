import { matchesQuery } from "./matches-query.js";

// The rows the scope picker shows, top to bottom: with nothing typed, the
// starred then recent scopes ({kind: "saved"}) and the tree with the nodes
// whose keys are in `open` unfolded; with text typed, the nodes whose
// label matches and the nodes around them, unfolded down to them. Each
// node row is {kind: "node", node, depth, parent, folds, unfolded}.
export function scopeRows(nodes, open, text, saved) {
  const typed = text.trim();
  const rows = typed === "" ? [...saved] : [];
  const walk = (list, depth, parent) => {
    for (const node of list) {
      const hit = typed === "" || matchesQuery(node.label.toLowerCase(), typed);
      const inner = [];
      const mark = rows.length;
      const unfolded = typed === "" ? open.has(node.key) : false;
      rows.push({ kind: "node", node, depth, parent, folds: node.children.length > 0, unfolded });
      if (typed !== "") {
        const before = rows.length;
        walk(node.children, depth + 1, node.key);
        inner.push(...rows.splice(before));
        if (!hit && inner.length === 0) {
          rows.splice(mark);
          continue;
        }
        rows[mark].unfolded = inner.length > 0;
        rows.push(...inner);
      } else if (unfolded) {
        walk(node.children, depth + 1, node.key);
      }
    }
  };
  walk(nodes, 0, null);
  return rows;
}
