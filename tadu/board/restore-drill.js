// Put back the filters, search, Blocked sub-chip and scope a portfolio
// drill-down replaced, once; a store without a pending drill-down is left
// alone.
export function restoreDrill(store) {
  if (store.beforeDrill === null) {
    return;
  }
  store.filters = store.beforeDrill.filters;
  store.text = store.beforeDrill.text;
  store.scope = store.beforeDrill.scope;
  store.where = store.beforeDrill.where;
  store.beforeDrill = null;
}
