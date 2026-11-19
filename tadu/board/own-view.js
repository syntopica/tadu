import { CALL_VIEWS } from "./call-views.js";

// Whether a view draws its own page (Changes and the tool call views)
// instead of the filtered cards, so the card toolbar, chips, summary and
// list head stay hidden.
export function ownView(view) {
  return view === "changes" || Object.hasOwn(CALL_VIEWS, view);
}
