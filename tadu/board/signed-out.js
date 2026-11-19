// Whether a failed load is the board saying the session has ended: its own
// 401 answer, not one from a proxy in front of it, which would loop.
export function signedOut(error) {
  return error.status === 401 && error.message === "signed out";
}
