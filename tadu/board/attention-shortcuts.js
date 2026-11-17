import { matchesWhere } from "./matches-where.js";
import { OPEN_COLUMNS } from "./open-columns.js";

// The sidebar's "Needs a person" entries: what waits on me (as `tadu inbox`
// has it, only with a `me`), then the open decisions, waiting and later
// items inside the scope, each with its count and the filters it applies.
export function attentionShortcuts(cards, where, me) {
  const open = cards.filter((card) => OPEN_COLUMNS.includes(card.column) && matchesWhere(card, where));
  const count = (test) => open.filter(test).length;
  const kind = (key, title, iconName) => ({
    key,
    title,
    iconName,
    count: count((card) => card.kind === key),
    filters: { kind: key },
  });
  const mine = {
    key: "mine",
    title: "Waiting on me",
    iconName: "user",
    count: count((card) => card.waiting_on_me === true),
    filters: { waitingOnMe: true },
  };
  return [
    ...(me ? [mine] : []),
    kind("decision", "Decisions", "alert"),
    kind("waiting", "Waiting on others", "clock"),
    kind("later", "Later", "calendar"),
  ];
}
