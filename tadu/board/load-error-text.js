// What the status line says when loading fails: without a token, a refusal
// points to the URL `tadu board` printed, and a refused token says it is
// missing or from an earlier run; an ended GitHub session asks to sign in
// again; otherwise "Load failed" the first time, "Reload failed" once data
// is on screen.
export function loadErrorText(error, loaded, noToken = false) {
  if (error.status === 403 && noToken) {
    return "No token: open the URL that `tadu board` printed.";
  }
  if (error.status === 403) {
    return "Access refused: open the URL that `tadu board` printed (the token is missing or from an earlier run).";
  }
  if (error.status === 401) {
    return "Signed out: reload the page to sign in with GitHub again.";
  }
  return `${loaded ? "Reload" : "Load"} failed: ${error.message}`;
}
