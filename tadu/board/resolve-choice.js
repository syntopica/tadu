// The offered value that typed `text` names: "" for empty text, the exact
// value, else the one value equal to it ignoring case, else the one value
// that contains it ignoring case; null when nothing or several match.
export function resolveChoice(text, values) {
  const typed = text.trim();
  if (typed === "") {
    return "";
  }
  if (values.includes(typed)) {
    return typed;
  }
  const lower = typed.toLowerCase();
  const same = values.filter((value) => value.toLowerCase() === lower);
  if (same.length === 1) {
    return same[0];
  }
  const containing = values.filter((value) =>
    value.toLowerCase().includes(lower),
  );
  return containing.length === 1 ? containing[0] : null;
}
