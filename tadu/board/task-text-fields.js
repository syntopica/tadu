// The text fields of a task file the detail panel shows, in the file's own
// order: each key with its title, its icon, and how its value reads: a
// line, Markdown lines (notes), one point per line, links or paths.
export const TASK_TEXT_FIELDS = [
  ["blocker", "Blocker", "alert", "line"],
  ["unblock", "To unblock", "arrowRight", "line"],
  ["notes", "Notes", "text", "text"],
  ["done_when", "Done when", "done", "points"],
  ["result", "Result", "done", "line"],
  ["evidence", "Evidence", "shield", "points"],
  ["resolution", "Resolution", "info", "line"],
  ["links", "Links", "external", "links"],
  ["files", "Files", "file", "paths"],
];
