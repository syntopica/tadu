import { el } from "./el.js";
import { icon } from "./icon.js";
import { plural } from "./plural.js";

// The parse problems of an item, with their count; null when it has none.
export function detailWarnings(card) {
  if (card.problems.length === 0) {
    return null;
  }
  const box = el("section", "warnings");
  const head = el("header", "warnings-head");
  head.append(
    icon("alert"),
    el("h3", "", "Parse warnings"),
    el("span", "muted", plural(card.problems.length, "warning")),
  );
  const list = el("ul");
  list.append(
    ...card.problems.map((problem) => el("li", "", `Line ${problem.line}: ${problem.message}`)),
  );
  box.append(head, list);
  return box;
}
