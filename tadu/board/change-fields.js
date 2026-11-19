// The properties the Changes view and an item's History filter by: the
// kind of change (Changes only), who made it, and the fields it changed.
export const CHANGE_FIELDS = [
  { key: "event", title: "Kind", icon: "layers", ops: ["any", "not"] },
  { key: "author", title: "Author", icon: "user", ops: ["any", "not"] },
  { key: "field", title: "Field", icon: "tag", ops: ["any", "not"] },
];
