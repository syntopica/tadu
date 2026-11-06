// Call `action` once `wait` ms have passed without another call.
export function debounce(action, wait) {
  let timer = 0;
  return (...args) => {
    window.clearTimeout(timer);
    timer = window.setTimeout(() => action(...args), wait);
  };
}
