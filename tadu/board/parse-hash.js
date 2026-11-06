// The scope and view a URL hash carries ("#company=x&project=y&view=board");
// `given` tells whether it carried any of them.
export function parseHash(hash) {
  const params = new URLSearchParams(hash.replace(/^#/, ""));
  const keys = ["company", "project", "repository", "view"];
  return {
    given: keys.some((key) => params.has(key)),
    where: {
      company: params.get("company") ?? "",
      project: params.get("project") ?? "",
      repository: params.get("repository") ?? "",
    },
    view: params.get("view"),
  };
}
