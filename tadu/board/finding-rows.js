import { el } from "./el.js";

// Doctor's findings (its --json objects), errors first: where, the code and
// what is wrong.
export function findingRows(findings) {
  const order = (finding) => (finding.severity === "error" ? 0 : 1);
  return [...findings]
    .sort((a, b) => order(a) - order(b))
    .map((finding) => {
      const row = el("p", `finding finding-${finding.severity}`);
      row.append(
        el("span", "finding-code", `${finding.severity} ${finding.code}`),
        el("span", "finding-place mono", `${finding.path}:${finding.line}`),
        el("span", "finding-message", finding.message),
      );
      return row;
    });
}
