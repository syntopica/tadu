// The browser's own parser decides the scheme, so tabs, newlines or case
// tricks inside "javascript:" cannot slip past the check.
export function urlScheme(url, base) {
  try {
    return new URL(url.trim(), base).protocol.toLowerCase();
  } catch {
    return null;
  }
}
