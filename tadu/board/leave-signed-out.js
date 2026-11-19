import { forgetBoard } from "./forget-board.js";

// The session ended (signed out here or in another tab, 14 days unused,
// refused by GitHub), or a token board's token no longer holds: no backlog
// text may stay on screen, as on a shared computer. Forget the data and empty
// the page at once, then load the address again: the server, for which the
// session is gone, answers it with the sign-in page, which keeps the view for
// the next sign-in (a token board says to open its printed URL). Reloading
// puts that page in the board's own history entry, so Back cannot show the
// board. (Going to "./#view=..." instead would only move to the hash.)
export function leaveSignedOut(store) {
  forgetBoard(store);
  window.location.reload();
}
