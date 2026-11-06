// The key J (step 1) or K (step -1) moves to; the first key when none is selected.
export function nextKey(keys, current, step) {
  if (keys.length === 0) {
    return null;
  }
  const index = keys.indexOf(current);
  if (index === -1) {
    return keys[0];
  }
  return keys[Math.min(Math.max(index + step, 0), keys.length - 1)];
}
