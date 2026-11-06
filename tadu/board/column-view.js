// Where a summary chip leads: Blocked and Done have their own views, the
// other states open All work filtered to that state.
export function columnView(column) {
  if (column === "blocked" || column === "done") {
    return { view: column, column: "" };
  }
  return { view: "all", column };
}
