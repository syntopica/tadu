// Split plain text at **bold** runs into text tokens {kind, text, strong};
// an unmatched marker stays literal and empty text produces no token.
export function tokenizeBold(source) {
  const tokens = [];
  let last = 0;
  for (const match of source.matchAll(/\*\*(?=\S)(.+?)\*\*/g)) {
    if (match.index > last) {
      tokens.push({ kind: "text", text: source.slice(last, match.index), strong: false });
    }
    tokens.push({ kind: "text", text: match[1], strong: true });
    last = match.index + match[0].length;
  }
  if (last < source.length) {
    tokens.push({ kind: "text", text: source.slice(last), strong: false });
  }
  return tokens;
}
