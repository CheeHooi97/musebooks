// Renders brand pages to PNG with Playwright: node brand/src/render.mjs <page.html> <out.png> <w> <h> [scale]
import { createRequire } from "node:module";
import path from "node:path";
import { pathToFileURL } from "node:url";
const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const [page, out, w, h, scale = "1"] = process.argv.slice(2);
const browser = await chromium.launch();
const tab = await browser.newPage({ viewport: { width: +w, height: +h }, deviceScaleFactor: +scale });
await tab.goto(pathToFileURL(path.resolve(page)).href, { waitUntil: "networkidle" });
await tab.evaluate(() => document.fonts.ready);
await tab.screenshot({ path: out, omitBackground: false });
await browser.close();
console.log(out);
