// The view a page starts in: the URL hash's when it names a known one, else
// the one this browser last used for the workspace, else the current one.
export function initialView(hashView, stored, views, current) {
  if (views.includes(hashView)) {
    return hashView;
  }
  return views.includes(stored) ? stored : current;
}
