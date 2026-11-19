import { boardToken } from "./board-token.js";
import { postOperation } from "./post-operation.js";

// Run a reading tool call and return its answer; a command that exits
// with another code than `codes` throws an Error with what it said on
// stderr, without its `tadu <name>: ` prefix (its `code` on the error).
export async function callOperation(name, args, codes = [0]) {
  const answer = await postOperation(boardToken(), name, args);
  if (!codes.includes(answer.code)) {
    const said = answer.errors.trim() || answer.output.trim() || `exit ${answer.code}`;
    const error = new Error(said.replace(`tadu ${name}: `, ""));
    error.code = answer.code;
    throw error;
  }
  return answer;
}
