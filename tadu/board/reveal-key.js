// Scroll the selected item into view: a drawn node directly, or a list row
// by its offset when the virtual list has not drawn it yet.
export function revealKey(store, key) {
  const node = [...document.querySelectorAll("#content [data-key]")].find(
    (n) => n.dataset.key === key,
  );
  if (node) {
    node.scrollIntoView({ block: "nearest" });
    node.focus({ preventScroll: true });
    return;
  }
  const list = store.list;
  const index = list?.rows.findIndex((row) => row.kind === "card" && row.card.key === key) ?? -1;
  if (index >= 0) {
    const top = list.spacer.getBoundingClientRect().top + window.scrollY + list.offsets[index];
    window.scrollTo(0, Math.max(top - window.innerHeight / 3, 0));
  }
}
