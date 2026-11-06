import { columnView } from "./column-view.js";

// Where a portfolio row leads under the portfolio's state filter: All work
// for every open state, or that state's own list.
export function portfolioTarget(state) {
  return state === "" ? { view: "all", column: "" } : columnView(state);
}
