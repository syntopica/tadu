// Keep a JSON value in this browser's localStorage; the page writes no file.
export function writeStored(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Storage full or disabled: the value lasts until the tab closes.
  }
}
