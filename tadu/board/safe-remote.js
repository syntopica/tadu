import { urlScheme } from "./url-scheme.js";

// A forge link is followed only when it is plain https.
export function safeRemote(url, base) {
  return typeof url === "string" && url.startsWith("https://") && urlScheme(url, base) === "https:";
}
