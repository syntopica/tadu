import { changeFieldInput } from "./change-field-input.js";
import { el } from "./el.js";
import { fieldFits } from "./field-fits.js";
import { icon } from "./icon.js";
import { inlineTitle } from "./inline-title.js";
import { openDetail } from "./open-detail.js";
import { previewText } from "./preview-text.js";
import { requestRender } from "./request-render.js";
import { returnFocus } from "./return-focus.js";
import { runChange } from "./run-change.js";

// The change dialog: the form is built once per change, so typing keeps
// its place; each render updates what tadu said, the similar items and
// whether the buttons wait on a call. Hidden with no change, and while a
// change without fields applies. While it shows, the page behind it is
// inert, and focus goes to its first field; closed, focus returns to what
// opened it.
export function renderChange(store) {
  const dialog = document.getElementById("change");
  const change = store.change;
  const shown = change !== null && !change.direct;
  document.getElementById("app").inert = shown;
  if (!shown) {
    if (!dialog.hidden) {
      returnFocus(dialog.shownChange?.opener);
    }
    dialog.hidden = true;
    dialog.shownChange = undefined;
    dialog.replaceChildren();
    return;
  }
  dialog.hidden = false;
  if (dialog.shownChange !== change) {
    dialog.shownChange = change;
    const close = el("button", "icon-button");
    close.type = "button";
    close.setAttribute("aria-label", "Close without changing (Esc)");
    close.append(icon("close"));
    close.addEventListener("click", () => {
      store.change = null;
      requestRender();
    });
    const head = el("header", "change-head");
    const title = el("h2", "", change.spec.title);
    title.id = "change-title";
    head.append(icon("edit"), title, close);
    const fields = el("div", "change-fields");
    fields.append(...change.spec.fields.map((field) => changeFieldInput(field, change.values)));
    const preview = el("button", "button", "Preview");
    preview.type = "button";
    preview.addEventListener("click", () => runChange(store, true));
    const apply = el("button", "button primary", "Apply");
    apply.type = "button";
    apply.addEventListener("click", () => runChange(store, false));
    const buttons = el("div", "change-buttons");
    buttons.append(preview, apply);
    const parts = {
      fields,
      error: el("p", "history-error change-error"),
      similar: el("div", "change-similar"),
      output: el("pre", "mono change-output"),
      buttons: [preview, apply],
    };
    parts.error.setAttribute("role", "alert");
    parts.output.setAttribute("aria-live", "polite");
    dialog.parts = parts;
    dialog.replaceChildren(head, fields, parts.error, parts.similar, parts.output, buttons);
    const first = fields.children[0]?.children[1];
    window.requestAnimationFrame(() => first?.focus());
  }
  const { fields, error, similar, output, buttons } = dialog.parts;
  for (const label of fields.children) {
    label.hidden = !fieldFits(change.spec, change.values, label.field);
  }
  error.textContent = change.error;
  error.hidden = change.error === "";
  similar.replaceChildren(
    ...(change.similar.length > 0 ? [el("p", "muted", "Open items most like it:")] : []),
    ...change.similar.map((item) => {
      const button = el("button", "link-button");
      button.type = "button";
      button.append(inlineTitle(item.title), ` (${item.repository})`);
      button.addEventListener("click", () => openDetail(item.key));
      return button;
    }),
  );
  output.textContent = previewText(change.output);
  output.hidden = change.output === "";
  for (const button of buttons) {
    button.disabled = change.busy;
  }
  dialog.setAttribute("aria-busy", String(change.busy));
}
