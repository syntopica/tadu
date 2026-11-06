import { COLUMN_TITLES } from "./column-titles.js";

// The heading of a column; Done names its window, "Done · 14 days".
export function columnTitle(column, doneDays) {
  const title = COLUMN_TITLES[column] ?? column;
  return column === "done" && doneDays ? `${title} · ${doneDays} days` : title;
}
