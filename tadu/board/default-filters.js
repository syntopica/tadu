// The filter choice with nothing selected; copy it before changing it.
// `rules` are the property filters, in the order they were added, each
// {field, op, values}: op "any" keeps an item with one of the values, "not"
// one with none of them, "empty" one with no value at all. Values of one
// rule are alternatives; every rule must hold. The company, project and
// repository are the chosen places (store.places), not filters.
export const DEFAULT_FILTERS = Object.freeze({
  rules: Object.freeze([]),
  waitingOnMe: false,
  showCancelled: false,
});
