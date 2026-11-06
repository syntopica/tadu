// What an empty list says, by view.
export function listEmptyText(view, filtered) {
  if (filtered) {
    return "Nothing matches the search and filters.";
  }
  return (
    {
      mine: "Nothing open is assigned to you.",
      blocked: "Nothing is blocked.",
      done: "Nothing was closed in this window.",
    }[view] ?? "Nothing to show."
  );
}
