import { shiftDay } from "./shift-day.js";

// The ranges of days a day-range button offers on `today`, each [title,
// since, until] ("" for an open end): for the Changes view the last 7, 14
// (its default, read from git with no days given) and 30 days, this month
// and last month; for a History, any time and the last 7, 30 and 90 days.
// "The last N days" runs from N days before today, as `tadu changes` and
// `--done-days` count them.
export function dayPresets(kind, today) {
  const month = today.slice(0, 8);
  const lastMonthEnd = shiftDay(`${month}01`, -1);
  if (kind === "changes") {
    return [
      ["Last 7 days", shiftDay(today, -7), ""],
      ["Last 14 days", "", ""],
      ["Last 30 days", shiftDay(today, -30), ""],
      ["This month", `${month}01`, ""],
      ["Last month", `${lastMonthEnd.slice(0, 8)}01`, lastMonthEnd],
    ];
  }
  return [
    ["Any time", "", ""],
    ["Last 7 days", shiftDay(today, -7), ""],
    ["Last 30 days", shiftDay(today, -30), ""],
    ["Last 90 days", shiftDay(today, -90), ""],
  ];
}
