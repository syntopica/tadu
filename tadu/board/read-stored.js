// A JSON value from this browser's localStorage; null when absent,
// unreadable or storage is disabled.
export function readStored(key) {
  try {
    return JSON.parse(window.localStorage.getItem(key) ?? "null");
  } catch {
    return null;
  }
}
