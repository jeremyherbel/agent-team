// Hidden eval check: copied in after the run; the agents never see it.
// Drives the real app in Chromium. Exits 77 (skipped) if Playwright is unavailable.
const { spawn } = require("node:child_process");
const path = require("node:path");

let chromium;
try {
  ({ chromium } = require("playwright"));
} catch {
  console.log("SKIP: playwright not installed (set NODE_PATH to a global node_modules that has it)");
  process.exit(77);
}

const port = 4100 + Math.floor(Math.random() * 800);
const root = path.resolve(__dirname, "..");

(async () => {
  const server = spawn(process.execPath, ["server.js"], { cwd: root, env: { ...process.env, PORT: String(port) }, stdio: "ignore" });
  let browser;
  try {
    await new Promise((r) => setTimeout(r, 700));
    browser = await chromium.launch();
    const page = await browser.newPage();
    await page.goto(`http://localhost:${port}/`);
    const counter = () => page.locator("#counter").innerText();
    const add = async (title) => {
      await page.locator("input:not([type=checkbox]):not([type=date])").first().fill(title);
      await page.keyboard.press("Enter");
    };
    const results = [];
    const expect = async (want) => results.push([want, (await counter()).trim()]);
    await expect("0 tasks left");
    await add("One");
    await expect("1 task left");
    await add("Two");
    await expect("2 tasks left");
    await page.locator("input[type=checkbox]").first().check();
    await expect("1 task left");
    const failed = results.filter(([want, got]) => want !== got);
    for (const [want, got] of results) console.log(`${want === got ? "ok  " : "FAIL"} expected ${JSON.stringify(want)}, got ${JSON.stringify(got)}`);
    process.exitCode = failed.length ? 1 : 0;
  } catch (e) {
    console.log("FAIL:", e.message);
    process.exitCode = 1;
  } finally {
    if (browser) await browser.close();
    server.kill();
  }
})();
