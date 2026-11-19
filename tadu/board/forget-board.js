// Drop everything the page knows of the backlog and empty the page, so that
// nothing of it stays on screen; nothing is drawn again on this page.
export function forgetBoard(store) {
  store.left = true;
  store.payload = null;
  store.cards = [];
  store.texts = new Map();
  store.byKey = new Map();
  store.index = null;
  store.list = null;
  document.body.replaceChildren();
}
