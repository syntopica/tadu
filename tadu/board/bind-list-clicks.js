// Let a popup's list take clicks without taking the focus from its search
// field: a click on an item (an element with data-at) calls
// `onItem(at, event)` with the item's place in the list.
export function bindListClicks(list, onItem) {
  list.addEventListener("mousedown", (event) => event.preventDefault());
  list.addEventListener("click", (event) => {
    const item = event.target.closest?.("[data-at]");
    if (item) {
      onItem(Number(item.dataset.at), event);
    }
  });
}
