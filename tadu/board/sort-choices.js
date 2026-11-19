// The orders a list offers, as [value, label]: Closing day only in Done.
export function sortChoices(view) {
  return [
    ["priority", "Priority"],
    ["due", "Due date"],
    ["title", "Title"],
    ["location", "Location"],
    ...(view === "done" ? [["closed", "Closing day"]] : []),
  ];
}
