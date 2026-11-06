import { boldMarkers } from "./bold-markers.js";
import { codeSpans } from "./code-spans.js";

// Inline Markdown of a title as tokens {kind: "text" | "code", text, strong}.
// Code spans are kept verbatim and ** inside them is never a marker, while
// bold may wrap code; anything else, unmatched markers included, is literal.
export function tokenizeInline(source) {
  const spans = codeSpans(source);
  const marks = boldMarkers(source, spans).map((start) => ({ start, end: start + 2 }));
  const events = [...marks, ...spans].sort((a, b) => a.start - b.start);
  const tokens = [];
  let strong = false;
  let last = 0;
  for (const event of events) {
    if (event.start > last) {
      tokens.push({ kind: "text", text: source.slice(last, event.start), strong });
    }
    if (event.text === undefined) {
      strong = !strong;
    } else {
      tokens.push({ kind: "code", text: event.text, strong });
    }
    last = event.end;
  }
  if (last < source.length) {
    tokens.push({ kind: "text", text: source.slice(last), strong });
  }
  return tokens;
}
