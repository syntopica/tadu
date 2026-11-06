const DAY_CEILING = 99999999;

// A string whose ascending order is the descending order of ISO days.
export function newestFirst(day) {
  return String(DAY_CEILING - Number(day.replaceAll("-", ""))).padStart(8, "0");
}
