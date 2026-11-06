// Every whitespace-separated term of the query occurs in the haystack.
export function matchesQuery(haystack, query) {
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  return terms.every((term) => haystack.includes(term));
}
