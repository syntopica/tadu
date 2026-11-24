// Drive the board page in a real Chromium, against a running board whose URL
// (with its token) is the first argument: block an item through the change
// dialog, drag a card to another column, add an item, and go through every
// view, light and dark, on a desktop and a phone. With a directory as the
// second argument, a screenshot of each step is saved there. The result is one
// JSON object: what the console reported, the requests that failed, and the
// notices the changes left. Chromium is CHROME_PATH, else the one
// @sparticuz/chromium unpacks (Linux).
import fs from "node:fs";
import puppeteer from "puppeteer-core";

const [url, out] = process.argv.slice(2);
const executablePath = process.env.CHROME_PATH ?? (await (await import("@sparticuz/chromium")).default.executablePath());
const browser = await puppeteer.launch({ executablePath, headless: true, args: ["--no-sandbox"] });
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const result = { console: [], failed: [], notices: [] };
if (out) {
  fs.mkdirSync(out, { recursive: true });
}

async function open(viewport, scheme, view) {
  const page = await browser.newPage();
  page.on("console", (message) => {
    // Chrome asks for /favicon.ico on its own; the board has none, and Chromium on Linux never asks.
    const favicon = message.location().url?.endsWith("/favicon.ico");
    if (["error", "warn"].includes(message.type()) && !favicon) result.console.push(message.text());
  });
  page.on("pageerror", (error) => result.console.push(error.message));
  page.on("response", (response) => {
    if (response.status() >= 400 && !response.url().endsWith("/favicon.ico")) result.failed.push(`${response.status()} ${response.request().method()} ${new URL(response.url()).pathname}`);
  });
  await page.bringToFront();
  await page.setViewport(viewport);
  await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: scheme }]);
  await page.goto(`${url}#view=${view}`, { waitUntil: "load" });
  await page.waitForFunction(() => document.getElementById("content").childElementCount > 0);
  await wait(300);
  return page;
}
const shot = async (page, name) => {
  if (out) {
    await wait(200);
    await page.screenshot({ path: `${out}/${name}.png` });
  }
};
const click = (page, scope, text) =>
  page.evaluate((s, t) => [...document.querySelectorAll(`${s} button`)].find((b) => b.textContent.startsWith(t)).click(), scope, text);
const notice = async (page) => {
  await page.waitForFunction(() => document.getElementById("notice").textContent !== "");
  result.notices.push(await page.$eval("#notice span", (node) => node.textContent));
  await page.click("#notice button");
  await page.waitForNetworkIdle({ idleTime: 100 });
};

const desktop = { width: 1440, height: 900 };
const page = await open(desktop, "light", "board");
await shot(page, "board");
await page.click(".card");
await page.waitForSelector("#detail details.history");
await page.evaluate(() => { document.querySelector("#detail details.history").open = true; });
await page.waitForSelector("#detail .history-entry, #detail .history-error");
await shot(page, "detail");
await click(page, "#detail .change-actions", "Edit");
await page.waitForSelector("#change:not([hidden])");
await shot(page, "edit-dialog");
await page.keyboard.press("Escape");
await page.waitForSelector("#change", { hidden: true });
await click(page, "#detail .change-actions", "Block");
await page.waitForSelector("#change input[name=note]");
await page.focus("#change input[name=note]");
await page.keyboard.type("Waiting on the payments team.");
await click(page, "#change", "Preview");
await page.waitForFunction(() => document.querySelector("#change .change-output").textContent !== "");
await shot(page, "block-preview");
await click(page, "#change", "Apply");
await notice(page);
await page.click("#detail .detail-head button");
await page.waitForNetworkIdle({ idleTime: 100 });
const source = await page.$("section.state-ready .card, section.state-backlog .card");
const target = await page.$("section.state-in_progress");
await page.setDragInterception(true);
await source.dragAndDrop(target);
await notice(page);
await page.setDragInterception(false);
await page.waitForNetworkIdle({ idleTime: 300 });
await page.click("#new-item");
await page.waitForSelector("#change input[name=title]");
// The dialog focuses its first field a frame after it opens; typing before that loses the rest of the title.
await page.waitForFunction(() => document.activeElement?.closest("#change"));
await page.focus("#change input[name=title]");
await page.keyboard.type("Fix the cart rounding");
await click(page, "#change", "Preview");
await page.waitForFunction(() => document.querySelector("#change .change-output").textContent !== "");
await shot(page, "new-item");
await click(page, "#change", "Apply");
await notice(page);
await page.click("#filter-add");
await page.waitForSelector("#filter-menu:not([hidden])");
await page.waitForFunction(() => document.activeElement?.closest("#filter-menu"));
await shot(page, "filter-menu");
await page.keyboard.type("priority");
await page.waitForSelector("#filter-menu-list .menu-option.field");
await page.keyboard.press("Enter");
await page.waitForSelector("#filter-menu-list .menu-option.value");
await page.keyboard.press("Enter");
await page.waitForSelector("#active-chips .filter-chip");
await page.keyboard.press("Escape");
await page.keyboard.press("Escape");
result.chips = await page.$$eval("#active-chips .filter-chip", (chips) => chips.map((chip) => chip.textContent));
await page.click("#display-button");
await shot(page, "display");
await page.click("[data-picker]");
await page.waitForSelector("#picker:not([hidden])");
await page.click("#picker-list .tree-row:not(.saved)");
await page.waitForFunction(() => window.location.hash.startsWith("#place="));
result.places = await page.evaluate(() => window.location.hash);
await shot(page, "scope");
await page.keyboard.press("Escape");
await page.close();
for (const scheme of ["light", "dark"]) {
  const viewPage = await open(desktop, scheme, "board");
  for (const view of ["mine", "all", "next", "urgent", "ready", "blocked", "portfolio", "done", "changes", "doctor", "board"]) {
    await viewPage.evaluate((name) => { window.location.hash = `#view=${name}`; }, view);
    await viewPage.waitForFunction((name) => document.body.dataset.view === name, {}, view);
    await viewPage.waitForNetworkIdle({ idleTime: 100 });
    await shot(viewPage, `${scheme}-${view}`);
  }
  await viewPage.close();
}
const phone = { width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2 };
for (const view of ["all", "next"]) {
  const phonePage = await open(phone, "light", view);
  result.phoneWidth = await phonePage.evaluate(() => document.documentElement.scrollWidth);
  await shot(phonePage, `phone-${view}`);
  if (view === "all") {
    await phonePage.click("#content [data-key]");
    await wait(300);
    result.phoneDetailWidth = await phonePage.evaluate(() => document.documentElement.scrollWidth);
    await shot(phonePage, "phone-detail");
  }
  await phonePage.close();
}
await browser.close();
process.stdout.write(JSON.stringify(result));
