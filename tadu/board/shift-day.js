// A YYYY-MM-DD day moved by `days` (negative for earlier), in UTC so no
// time zone or daylight change shifts it.
export function shiftDay(day, days) {
  const date = new Date(`${day}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}
