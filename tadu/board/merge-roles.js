// Add roles not yet listed, keeping first-seen order.
export function mergeRoles(target, roles) {
  for (const role of roles) {
    if (!target.includes(role)) {
      target.push(role);
    }
  }
}
