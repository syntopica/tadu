// The places and view a URL hash carries ("#place=company:x&place=
// repository:y&view=board"), or one place by level as links made before
// several places could be chosen ("#company=x&project=y"); `given` tells
// whether it carried any of them.
export function parseHash(hash) {
  const params = new URLSearchParams(hash.replace(/^#/, ""));
  const levels = ["company", "project", "repository"];
  const blank = { company: "", project: "", repository: "" };
  const places = params.getAll("place").flatMap((text) => {
    const [level, ...key] = text.split(":");
    return levels.includes(level) ? [{ ...blank, [level]: key.join(":") }] : [];
  });
  if (places.length === 0 && levels.some((level) => params.has(level))) {
    places.push(Object.fromEntries(levels.map((level) => [level, params.get(level) ?? ""])));
  }
  return {
    given: places.length > 0 || params.has("view") || params.has("place"),
    places,
    view: params.get("view"),
  };
}
