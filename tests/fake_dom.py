"""A small DOM for board modules run under node: enough for the detail panel and its history."""

FAKE_DOM = r"""
class ClassList {
  constructor(node) { this.node = node; }
  names() { return this.node.className.split(" ").filter(Boolean); }
  add(name) { if (!this.contains(name)) this.node.className = [...this.names(), name].join(" "); }
  remove(name) { this.node.className = this.names().filter((n) => n !== name).join(" "); }
  contains(name) { return this.names().includes(name); }
  toggle(name, on) {
    const wanted = on ?? !this.contains(name);
    if (wanted) this.add(name); else this.remove(name);
    return wanted;
  }
}

class Node {
  constructor(tag) {
    this.tagName = tag.toUpperCase();
    this.className = "";
    this.classList = new ClassList(this);
    this.children = [];
    this.parentNode = null;
    this.attributes = {};
    this.dataset = {};
    this.listeners = {};
    this.ownText = "";
    this.hidden = false;
    this.value = "";
    this.selected = false;
    this.openState = false;
    this.styles = {};
    this.style = { setProperty: (name, value) => { this.styles[name] = value; } };
  }
  get open() { return this.openState; }
  set open(value) {
    const changed = Boolean(value) !== this.openState;
    this.openState = Boolean(value);
    if (changed) setTimeout(() => this.dispatch("toggle"), 0);
  }
  get textContent() { return this.ownText + this.children.map((c) => c.textContent).join(""); }
  set textContent(text) { this.children = []; this.ownText = String(text); }
  get options() { return this.children.filter((c) => c.tagName === "OPTION"); }
  get childElementCount() { return this.children.filter((c) => c.tagName !== "#TEXT").length; }
  get isConnected() {
    let node = this;
    while (node.parentNode) node = node.parentNode;
    return node === document.body || node.attached === true;
  }
  append(...nodes) {
    for (const node of nodes) {
      if (node.tagName === "#FRAGMENT") {
        this.append(...node.children);
        continue;
      }
      const child = typeof node === "string" ? Object.assign(new Node("#text"), { ownText: node }) : node;
      child.parentNode = this;
      this.children.push(child);
    }
  }
  replaceChildren(...nodes) {
    for (const child of this.children) child.parentNode = null;
    this.children = [];
    this.append(...nodes);
  }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; }
  getBoundingClientRect() { return { left: 10, top: 20, right: 110, bottom: 50, width: 100, height: 30 }; }
  scrollIntoView() {}
  getAttribute(name) { return this.attributes[name] ?? null; }
  addEventListener(name, fn) { (this.listeners[name] ??= []).push(fn); }
  dispatch(name, event = {}) { for (const fn of this.listeners[name] ?? []) fn({ target: this, ...event }); }
  click() { this.dispatch("click"); }
  focus() {}
  matches(selector) {
    if (selector.includes(",")) return selector.split(",").some((part) => this.matches(part.trim()));
    if (selector.startsWith("#")) return this.id === selector.slice(1);
    const found = /^([a-z0-9]*)((?:\.[\w-]+)*)(?:\[([\w-]+)(?:="([^"]*)")?\])?$/.exec(selector);
    if (!found) throw new Error(`unsupported selector ${selector}`);
    const [, tag, classes, attr, value] = found;
    if (tag && this.tagName !== tag.toUpperCase()) return false;
    for (const name of classes.split(".").filter(Boolean)) if (!this.classList.contains(name)) return false;
    const data = attr?.startsWith("data-")
      ? this.dataset[attr.slice(5).replace(/-(\w)/g, (_, c) => c.toUpperCase())]
      : undefined;
    const given = data ?? this[attr] ?? this.attributes[attr];
    if (attr && value === undefined && given === undefined) return false;
    if (attr && value !== undefined && String(given) !== value) return false;
    return true;
  }
  querySelectorAll(selector) {
    const found = [];
    const walk = (node) => {
      for (const child of node.children) {
        if (child.matches(selector)) found.push(child);
        walk(child);
      }
    };
    walk(this);
    return found;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] ?? null; }
  contains(node) {
    for (let at = node; at; at = at.parentNode) if (at === this) return true;
    return false;
  }
  closest(selector) {
    let node = this;
    while (node && node.matches) {
      if (node.matches(selector)) return node;
      node = node.parentNode;
    }
    return null;
  }
}

const ids = {};
const storage = new Map();
globalThis.document = {
  body: new Node("body"),
  createElement: (tag) => new Node(tag),
  createElementNS: (_, tag) => new Node(tag),
  createDocumentFragment: () => new Node("#fragment"),
  createTextNode: (text) => Object.assign(new Node("#text"), { ownText: String(text) }),
  getElementById: (id) => (ids[id] ??= Object.assign(new Node("div"), { attached: true, id })),
  querySelectorAll: (selector) => document.body.querySelectorAll(selector),
  listeners: {},
  addEventListener(name, fn) { (this.listeners[name] ??= []).push(fn); },
  dispatch(name, event) { for (const fn of this.listeners[name] ?? []) fn(event); },
};
globalThis.window = {
  location: { href: "http://127.0.0.1:41000/", search: "", hash: "" },
  sessionStorage: {
    getItem: (key) => storage.get(key) ?? null,
    setItem: (key, value) => storage.set(key, String(value)),
  },
  history: { replaceState: () => {} },
  requestAnimationFrame: (fn) => setTimeout(fn, 0),
  innerWidth: 1280,
  dispatchEvent: (event) => renders.push(event.type),
};
const renders = [];
const requests = [];
const responses = [];
globalThis.fetch = async (url, options) => {
  const request = { url, token: options.headers["X-Tadu-Token"], cache: options.cache };
  if (options.method !== undefined) {
    Object.assign(request, { method: options.method, type: options.headers["Content-Type"], body: JSON.parse(options.body) });
  }
  requests.push(request);
  const [status, body] = responses.shift() ?? [404, { error: "no response queued" }];
  return { ok: status >= 200 && status < 300, status, json: async () => body };
};
const answer = (output, errors = "", code = 0) => [200, { code, output, errors }];
const settle = () => new Promise((resolve) => setTimeout(resolve, 5));
const texts = (node, selector) => node.querySelectorAll(selector).map((n) => n.textContent);
"""
