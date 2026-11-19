import { forgetBoard } from "./forget-board.js";

// The board stopped answering: its data may be stale and nobody can check
// that the session still holds, so the page shows nothing of it, only this
// notice, until the board answers again and the page reloads.
export function showUnreachable(store) {
  forgetBoard(store);
  const main = document.createElement("main");
  main.className = "login";
  const card = document.createElement("div");
  card.className = "login-card";
  const title = document.createElement("h1");
  title.textContent = "The board cannot be reached";
  const text = document.createElement("p");
  text.className = "muted";
  text.textContent =
    "Nothing of it is shown until it answers again. This page reloads by itself when it does.";
  card.append(title, text);
  main.append(card);
  document.body.append(main);
  document.title = "Unreachable · tadu";
}
