import { DEFAULT_FILTERS } from "./default-filters.js";

// The page's one mutable state. Renderers read it; actions change it and
// call requestRender().
export const store = {
  payload: null,
  cards: [],
  texts: new Map(),
  byKey: new Map(),
  error: "",
  loading: false,
  view: "board",
  text: "",
  filters: { ...DEFAULT_FILTERS },
  scope: "all",
  group: "state",
  sort: "priority",
  showEmpty: false,
  collapsed: new Set(),
  selected: null,
  detail: false,
  focusDetail: false,
  navKeys: [],
  portfolio: { text: "", groupBy: "organization", role: "", state: "", collapsed: new Set() },
  saved: [],
  theme: "auto",
  navOpen: false,
  problemsOpen: false,
};
