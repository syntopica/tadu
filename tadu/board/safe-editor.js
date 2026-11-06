import { BLOCKED_SCHEMES } from "./blocked-schemes.js";
import { urlScheme } from "./url-scheme.js";

// An editor link may use any scheme the browser parses, except script ones.
export function safeEditor(url, base) {
  if (typeof url !== "string") {
    return false;
  }
  const found = urlScheme(url, base);
  return found !== null && !BLOCKED_SCHEMES.includes(found);
}
