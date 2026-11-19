import { currentSets } from "./current-sets.js";
import { fieldValues } from "./field-values.js";
import { matchesRule } from "./matches-rule.js";
import { offeredFields } from "./offered-fields.js";
import { QUICK_FILTERS } from "./quick-filters.js";
import { requestRender } from "./request-render.js";
import { setRule } from "./set-rule.js";

// What the Filter menu filters on a list or the board: the item fields the
// cards in view offer, their values counted over those cards (the search
// and scope applied, no filter), the quick filters, and store.filters.
export function itemFilterSource(store) {
  const payload = store.payload;
  const me = payload.me ?? null;
  const today = payload.today;
  // The cards counted change only with the search, scope, view and cancelled items shown.
  let memo = null;
  const cards = () => {
    const key = [store.cards, store.text, store.places, store.view, store.scope, store.filters.showCancelled];
    if (memo === null || memo.key.some((value, at) => value !== key[at])) {
      memo = { key, value: currentSets(store).base };
    }
    return memo.value;
  };
  const change = (filters) => {
    store.filters = { ...store.filters, ...filters };
    requestRender();
  };
  const resolve = (rule) => ({ ...rule, values: rule.values.map((value) => (value === "@me" ? me : value)) });
  const quick = () =>
    QUICK_FILTERS.filter((entry) => me !== null || !entry.me).map((entry) => {
      const rule = entry.rule ? resolve(entry.rule) : null;
      const own = store.filters.rules.find((old) => old.field === rule?.field);
      const active = rule ? JSON.stringify(own) === JSON.stringify(rule) : store.filters.waitingOnMe;
      const holds = (card) => (rule ? matchesRule(card, rule, today) : card.waiting_on_me === true);
      return {
        key: entry.key,
        title: entry.title,
        icon: entry.icon,
        count: cards().filter(holds).length,
        active,
        apply: () => {
          if (rule === null) {
            change({ waitingOnMe: !active });
          } else {
            const rules = store.filters.rules.filter((old) => old.field !== rule.field);
            change({ rules: active ? rules : setRule(rules, rule) });
          }
        },
      };
    });
  const context = { today, columns: payload.columns, names: store.index.orgNames, me };
  return {
    fields: () => offeredFields(cards()),
    values: (field, chosen) => fieldValues(field, cards(), context, chosen),
    quick,
    rules: () => store.filters.rules,
    change: (rules) => change({ rules }),
  };
}
