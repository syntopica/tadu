// Plain code-point order, stable across locales.
export function compareText(a, b) {
  if (a === b) {
    return 0;
  }
  return a < b ? -1 : 1;
}
