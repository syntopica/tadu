// What counts as a person's activity on an open board: pressing, typing,
// scrolling with a wheel or a finger. Mere pointer moves do not, so a mouse
// nudged on a shared desk keeps nobody signed in.
export const ACTIVITY_EVENTS = ["pointerdown", "keydown", "wheel", "touchstart"];
