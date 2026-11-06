// A string whose ascending order is the descending order of ISO days.
export function newestFirst(day) {
  const ceiling = 99999999;
  return String(ceiling - Number(day.replaceAll("-", ""))).padStart(8, "0");
}
