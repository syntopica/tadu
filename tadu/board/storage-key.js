// localStorage key of one kind of board state ("scope", "recent",
// "favourites") for one workspace in this browser.
export function storageKey(name, workspaceId) {
  return `tadu_board_${name}:${workspaceId}`;
}
