// The objects of a command's --json output: one JSON object per line.
export function jsonLines(text) {
  return text
    .split("\n")
    .filter((line) => line.trim() !== "")
    .map((line) => JSON.parse(line));
}
