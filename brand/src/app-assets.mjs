// Writes the Collector's Index logo into the website and the Capacitor source
// images (frontend/resources) that @capacitor/assets turns into native icons.
// node brand/src/app-assets.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { indexMark, THEME } from "./index-mark.mjs";

const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const frontend = path.resolve(brand, "../frontend");
const { light: L, dark: D } = THEME;

// Browser-tab icon: bars follow the tab's colour scheme so they never vanish on dark chrome.
fs.writeFileSync(path.join(frontend, "public/favicon.svg"), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
<style>.b{fill:${L.ink}}.d{fill:${L.accent}}@media (prefers-color-scheme:dark){.b{fill:${D.ink}}.d{fill:${D.accent}}}</style>
<g class="b"><rect x="16" y="39" width="16" height="60" rx="8"/><rect x="40" y="55" width="16" height="44" rx="8"/><rect x="64" y="55" width="16" height="44" rx="8"/><rect x="88" y="39" width="16" height="60" rx="8"/></g>
<circle class="d" cx="96" cy="27" r="6.5"/></svg>\n`);

const square = (bg, markSize, theme, w = 1024) => `<body style="margin:0;width:${w}px;height:${w}px;display:grid;place-items:center;background:${bg}">${indexMark({ theme, size: markSize })}</body>`;
const jobs = [
  // Website fallbacks for browsers without SVG favicons, and the iOS home-screen bookmark.
  [path.join(frontend, "public/favicon.png"), 512, `<body style="margin:0;width:512px;height:512px;display:grid;place-items:center;background:transparent"><div style="width:512px;height:512px;border-radius:112px;background:${L.bg};display:grid;place-items:center">${indexMark({ size: 400 })}</div></body>`, true],
  [path.join(frontend, "public/apple-touch-icon.png"), 180, square(L.bg, 140, "light", 180)],
  // Capacitor sources: full icon, adaptive foreground (inside the 66% safe zone) and background, splashes.
  [path.join(frontend, "resources/icon-only.png"), 1024, square(D.bg, 760, "dark")],
  [path.join(frontend, "resources/icon-foreground.png"), 1024, `<body style="margin:0;width:1024px;height:1024px;display:grid;place-items:center;background:transparent">${indexMark({ theme: "dark", size: 560 })}</body>`, true],
  [path.join(frontend, "resources/icon-background.png"), 1024, `<body style="margin:0;width:1024px;height:1024px;background:${D.bg}"></body>`],
  [path.join(frontend, "resources/splash.png"), 2732, square(L.bg, 520, "light", 2732)],
  [path.join(frontend, "resources/splash-dark.png"), 2732, square(D.bg, 520, "dark", 2732)],
];

fs.mkdirSync(path.join(frontend, "resources"), { recursive: true });
const browser = await chromium.launch();
for (const [file, size, body, transparent] of jobs) {
  const tab = await browser.newPage({ viewport: { width: size, height: size } });
  await tab.setContent(`<!doctype html><meta charset="utf-8">${body}`);
  await tab.screenshot({ path: file, omitBackground: !!transparent });
  await tab.close();
  console.log(path.relative(brand, file));
}
await browser.close();
