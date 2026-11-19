import { leaveSignedOut } from "./leave-signed-out.js";
import { responseBody } from "./response-body.js";
import { signedOut } from "./signed-out.js";
import { store } from "./store.js";

// POST one tool call as JSON, relative to the page, with the per-run token in
// a header when the page has one (a board that signs in with GitHub knows the
// person by their session): the server runs it as `tadu mcp` does, over the
// board's workspace (for a signed-in person, over the repositories they read).
// The answer is the command's exit `code`, `output` and `errors`; a refused
// call (such as a change the board's --allow does not permit) throws as
// responseBody does, and an ended session leaves for the sign-in page.
export async function postOperation(token, name, args) {
  const response = await fetch(`api/op/${encodeURIComponent(name)}`, {
    method: "POST",
    cache: "no-store",
    headers: { ...(token ? { "X-Tadu-Token": token } : {}), "Content-Type": "application/json" },
    body: JSON.stringify(args),
  });
  try {
    return await responseBody(response);
  } catch (error) {
    if (signedOut(error)) {
      leaveSignedOut(store);
    }
    throw error;
  }
}
