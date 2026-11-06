import { COLUMN_TITLES } from "./column-titles.js";
import { el } from "./el.js";

// A coloured pill naming a card's column.
export function statePill(column) {
  const pill = el("span", `state-pill state-${column}`);
  pill.append(el("span", "dot"), el("span", "", COLUMN_TITLES[column] ?? column));
  return pill;
}
