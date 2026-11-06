// What the status line says when loading fails: a refused token points back
// to the printed URL; otherwise "Load failed" the first time, "Reload
// failed" once data is on screen.
export function loadErrorText(error, loaded) {
  if (error.status === 403) {
    return "Access refused: open the URL that `tadu board` printed (the token is missing or from an earlier run).";
  }
  return `${loaded ? "Reload" : "Load"} failed: ${error.message}`;
}
