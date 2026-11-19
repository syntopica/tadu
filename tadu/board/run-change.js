import { boardToken } from "./board-token.js";
import { changeArguments } from "./change-arguments.js";
import { changeOutcome } from "./change-outcome.js";
import { clearedField } from "./cleared-field.js";
import { jsonLines } from "./json-lines.js";
import { loadBoard } from "./load-board.js";
import { postOperation } from "./post-operation.js";
import { requestRender } from "./request-render.js";

// Preview or apply the open change. A preview shows what tadu would write
// (and, for a new item, the open items most like it); an applied change
// closes the dialog (unless another change replaced it meanwhile), says so
// (and whether doctor then found errors), and reloads the board. A refusal
// keeps the dialog open with what tadu said. The similar items are a help: when they cannot be read, none show.
export async function runChange(store, preview) {
  const change = store.change;
  const missing = change.spec.fields.find(
    (field) => field.required && String(change.values[field.name] ?? "").trim() === "",
  );
  const cleared = clearedField(change.spec, change.values);
  if (missing || cleared) {
    change.error = missing
      ? `${missing.label} is needed.`
      : `${cleared.label} cannot be emptied here; open the item in the editor to remove it.`;
    requestRender();
    return;
  }
  change.busy = true;
  change.error = "";
  requestRender();
  const token = boardToken();
  try {
    const args = changeArguments(change.spec, change.values);
    const answer = await postOperation(token, change.spec.operation, preview ? { ...args, preview: true } : args);
    change.output = (answer.output + answer.errors).trim();
    if (preview && change.spec.similar && answer.code === 0) {
      const asked = { text: args.title, repository: args.repository, open: true, limit: 5, json: true };
      const found = await postOperation(token, "similar", asked).catch(() => ({ output: "" }));
      change.similar = jsonLines(found.output);
    }
    const outcome = changeOutcome(answer.code, preview);
    if (outcome === "refused") {
      change.error = "tadu refused the change.";
      change.direct = false;
    } else if (!preview) {
      // Written: a doctor error left in the backlog must not invite the same change twice.
      if (store.change === change) {
        store.change = null;
      }
      const warned = outcome === "warned" ? " tadu doctor reports errors in this backlog; see Doctor." : "";
      const output = answer.output.trim();
      // A team board proposes the change (a pull request or an issue) instead of writing it.
      const result = output.startsWith("proposed: ") ? output : "done.";
      store.notice = `${change.spec.title}: ${result}${warned}`;
      loadBoard();
    }
  } catch (error) {
    change.error =
      error.status === 403 ? `Not allowed: ${error.message}.` : `The change failed: ${error.message}`;
    change.direct = false;
  } finally {
    change.busy = false;
    requestRender();
  }
}
