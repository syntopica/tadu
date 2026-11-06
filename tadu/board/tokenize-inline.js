import { tokenizeCode } from "./tokenize-code.js";

// Inline Markdown of a title as tokens {kind: "text" | "code", text, strong}.
// Only **bold** and `code` are recognised, code also inside bold; anything
// else, unmatched markers included, stays literal text.
export function tokenizeInline(source) {
  const pattern = /\*\*(?=\S)(.+?)\*\*/g;
  const tokens = [];
  let last = 0;
  for (const match of source.matchAll(pattern)) {
    tokens.push(...tokenizeCode(source.slice(last, match.index), false));
    tokens.push(...tokenizeCode(match[1], true));
    last = match.index + match[0].length;
  }
  tokens.push(...tokenizeCode(source.slice(last), false));
  return tokens;
}
