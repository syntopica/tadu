// The fields of a format 2 card's task file, read from its text; null for
// a TODO.md item, or a file that is not a JSON object (doctor reports it).
export function taskFile(card) {
  if (!card.path.endsWith(".json")) {
    return null;
  }
  try {
    const task = JSON.parse(card.text);
    return task !== null && typeof task === "object" && !Array.isArray(task) ? task : null;
  } catch {
    return null;
  }
}
