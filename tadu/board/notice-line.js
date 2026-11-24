import { el } from "./el.js";
import { externalLink } from "./external-link.js";
import { safeRemote } from "./safe-remote.js";

// The notice's text as a line: every https URL in it that safeRemote accepts
// becomes a link; the rest stays text. Text goes in as text nodes and the
// link's address is set as a property, so nothing in the notice is parsed as HTML.
export function noticeLine(text) {
  const line = el("span");
  let from = 0;
  for (const found of text.matchAll(/https:\/\/[^\s<>"]+/g)) {
    // Sentence punctuation after the address is not part of it.
    const url = found[0].replace(/[).,;:]+$/, "");
    if (!safeRemote(url, window.location.href)) {
      continue;
    }
    line.append(document.createTextNode(text.slice(from, found.index)));
    line.append(externalLink(url, url, "notice-link"));
    from = found.index + url.length;
  }
  line.append(document.createTextNode(text.slice(from)));
  return line;
}
