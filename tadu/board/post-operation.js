import { responseBody } from "./response-body.js";

// POST one tool call with the per-run token in a header, as JSON: the
// server runs it as `tadu mcp` does, over the board's workspace. The answer
// is the command's exit `code`, `output` and `errors`; a refused call (such
// as a change the board's --allow does not permit) throws as responseBody
// does.
export async function postOperation(token, name, args) {
  const response = await fetch(`/api/op/${encodeURIComponent(name)}`, {
    method: "POST",
    cache: "no-store",
    headers: { "X-Tadu-Token": token, "Content-Type": "application/json" },
    body: JSON.stringify(args),
  });
  return responseBody(response);
}
