// Whether a form field applies: one that only a backlog format takes shows
// for a repository of that format (`spec.formats`, by the chosen
// repository); any other field always does.
export function fieldFits(spec, values, field) {
  const format = spec.formats?.[values.repository];
  return !field.format || format === undefined || field.format === format;
}
