// Split plain text at `code` spans into tokens {kind, text, strong}; empty
// text produces no token.
export function tokenizeCode(source, strong) {
  const tokens = [];
  let last = 0;
  for (const match of source.matchAll(/`([^`]+)`/g)) {
    if (match.index > last) {
      tokens.push({ kind: "text", text: source.slice(last, match.index), strong });
    }
    tokens.push({ kind: "code", text: match[1], strong });
    last = match.index + match[0].length;
  }
  if (last < source.length) {
    tokens.push({ kind: "text", text: source.slice(last), strong });
  }
  return tokens;
}
