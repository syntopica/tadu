// Ask for one render on the next frame; repeated calls in a frame coalesce.
export function requestRender() {
  if (requestRender.pending) {
    return;
  }
  requestRender.pending = true;
  window.requestAnimationFrame(() => {
    requestRender.pending = false;
    window.dispatchEvent(new Event("tadu:render"));
  });
}
