import { callOperation } from "./call-operation.js";
import { changeDays } from "./change-days.js";
import { jsonLines } from "./json-lines.js";

// The workspace's changes of the chosen days (the last 14 when none are
// chosen) as `tadu changes --json` gives them, with the days read and the
// repositories git could not read; throws as callOperation does.
export async function fetchChanges(since, until, today) {
  const days = changeDays(since, until, today);
  const answer = await callOperation("changes", { ...days, json: true });
  const problems = answer.errors
    .split("\n")
    .filter((line) => line.trim() !== "")
    .map((line) => line.replace(/^tadu changes: /, ""));
  return { ...days, today, changes: jsonLines(answer.output), problems };
}
