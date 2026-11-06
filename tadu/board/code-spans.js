// Every `code` span of a title as {start, end, text}; end is exclusive and
// covers the closing backtick.
export function codeSpans(source) {
  return [...source.matchAll(/`([^`]+)`/g)].map((match) => ({
    start: match.index,
    end: match.index + match[0].length,
    text: match[1],
  }));
}
