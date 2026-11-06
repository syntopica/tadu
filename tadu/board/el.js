// A new element with an optional class and text; text is always set as
// textContent, never parsed as HTML.
export function el(tag, className = "", text = undefined) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined) {
    node.textContent = text;
  }
  return node;
}
