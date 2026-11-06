// Start offsets of the ** markers outside code spans that pair into bold runs:
// an opener is followed by a non-space character, the next marker closes it,
// and a marker left unpaired is not returned, so it stays literal text.
export function boldMarkers(source, spans) {
  const outside = (index) => spans.every((span) => index + 2 <= span.start || index >= span.end);
  const paired = [];
  let open = null;
  for (const match of source.matchAll(/\*\*/g)) {
    const index = match.index;
    if (!outside(index)) {
      continue;
    }
    if (open === null) {
      if (/\S/.test(source[index + 2] ?? "") && source[index + 2] !== "*") {
        open = index;
      }
    } else if (index > open + 2) {
      paired.push(open, index);
      open = null;
    }
  }
  return paired;
}
