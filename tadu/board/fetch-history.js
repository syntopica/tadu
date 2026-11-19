import { callOperation } from "./call-operation.js";

// One item's history, as `tadu show --history --json` gives it, and whether
// the clone is shallow; throws as callOperation does.
export async function fetchHistory(card) {
  const args = { key: card.key, repository: card.repository, history: true, json: true };
  const answer = await callOperation("show", args);
  const { history, shallow } = JSON.parse(answer.output);
  return { history, shallow };
}
