// What the page says when a request fails: a refused token (403) points back
// to the URL `tadu board` printed; anything else is `what` and the reason.
export function failureText(error, what) {
  if (error.status === 403) {
    return "Access refused: open the URL that `tadu board` printed (the token is missing or from an earlier run).";
  }
  return `${what}: ${error.message}`;
}
