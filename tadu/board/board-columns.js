// The columns the board draws: empty ones only when empty columns are
// shown, Cancelled only when toggled on.
export function boardColumns(columns, counts, showEmpty, showCancelled) {
  return columns.filter((column) => {
    if (column === "cancelled" && !showCancelled) {
      return false;
    }
    return showEmpty || counts[column] > 0;
  });
}
