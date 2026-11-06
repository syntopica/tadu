// An ISO time as local "HH:MM"; "" when it does not parse.
export function formatClock(iso) {
  const time = new Date(iso);
  if (Number.isNaN(time.getTime())) {
    return "";
  }
  const pad = (value) => String(value).padStart(2, "0");
  return `${pad(time.getHours())}:${pad(time.getMinutes())}`;
}
