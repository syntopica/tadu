import { callOperation } from "./call-operation.js";
import { CALL_VIEWS } from "./call-views.js";
import { loadOnce } from "./load-once.js";

// Run a view's tool call once for `key` (the view and the board load it
// belongs to) into store.calls[view], as loadOnce does; an exit code the
// view does not expect is its error, with what the command said.
export async function loadCall(store, view, key) {
  const spec = CALL_VIEWS[view];
  store.calls[view] ??= {};
  await loadOnce(
    store.calls[view],
    key,
    () => callOperation(spec.operation, spec.args, spec.codes),
    "Unavailable",
  );
}
