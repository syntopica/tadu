import { drillFromPortfolio } from "./drill-from-portfolio.js";
import { portfolioTarget } from "./portfolio-target.js";

// What clicking a portfolio row does: open its items in its scope (or with
// its relation filter) in the list for the portfolio's state filter, or the
// Blocked view when `blocked`. Null for a row that opens nothing.
export function portfolioDrill(node, state) {
  if (!node.target && !node.filter) {
    return null;
  }
  return (blocked) => {
    const target = blocked ? { view: "blocked", column: "" } : portfolioTarget(state);
    drillFromPortfolio(node.target ?? null, node.filter ?? null, target.view, target.column);
  };
}
