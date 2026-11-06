import { el } from "./el.js";
import { icon } from "./icon.js";

// A link that opens in a new tab with no opener and no referrer. The caller
// has already checked the URL with safeEditor or safeRemote.
export function externalLink(label, url, className) {
  const anchor = el("a", className);
  anchor.href = url;
  anchor.rel = "noopener noreferrer";
  anchor.target = "_blank";
  anchor.append(icon("external"), el("span", "", label));
  return anchor;
}
