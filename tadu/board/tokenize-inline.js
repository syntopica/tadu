// Inline Markdown of a title as tokens: {kind: "text" | "strong" | "code",
// text}. Only **bold** and `code` are recognised; anything else, unmatched
// markers included, stays literal text.
export function tokenizeInline(source) {
  const pattern = /`([^`]+)`|\*\*(?=\S)(.+?)\*\*/g;
  const tokens = [];
  let last = 0;
  for (const match of source.matchAll(pattern)) {
    if (match.index > last) {
      tokens.push({ kind: "text", text: source.slice(last, match.index) });
    }
    if (match[1] !== undefined) {
      tokens.push({ kind: "code", text: match[1] });
    } else {
      tokens.push({ kind: "strong", text: match[2] });
    }
    last = match.index + match[0].length;
  }
  if (last < source.length) {
    tokens.push({ kind: "text", text: source.slice(last) });
  }
  return tokens;
}
