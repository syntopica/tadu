import { tokenizeInline } from "./tokenize-inline.js";

// A title's **bold** and `code` as <strong> and <code> holding text nodes;
// everything else is literal text.
export function inlineTitle(source) {
  const fragment = document.createDocumentFragment();
  for (const token of tokenizeInline(source)) {
    let node = document.createTextNode(token.text);
    if (token.kind === "code") {
      const code = document.createElement("code");
      code.append(node);
      node = code;
    }
    if (token.strong) {
      const strong = document.createElement("strong");
      strong.append(node);
      node = strong;
    }
    fragment.append(node);
  }
  return fragment;
}
