import { tokenizeBold } from "./tokenize-bold.js";

// Inline Markdown of a title as tokens {kind: "text" | "code", text, strong}.
// Code spans are found first and kept verbatim, then **bold** only in the
// text between them; anything else, unmatched markers included, is literal.
export function tokenizeInline(source) {
  const tokens = [];
  let last = 0;
  for (const match of source.matchAll(/`([^`]+)`/g)) {
    tokens.push(...tokenizeBold(source.slice(last, match.index)));
    tokens.push({ kind: "code", text: match[1], strong: false });
    last = match.index + match[0].length;
  }
  tokens.push(...tokenizeBold(source.slice(last)));
  return tokens;
}
