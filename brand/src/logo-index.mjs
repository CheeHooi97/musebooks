// Logo deliverables for the Collector's Index mark, for approval only (no store art).
// node brand/src/logo-index.mjs  ->  brand/logo/
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { indexMark, THEME } from "./index-mark.mjs";
import { fontCSS } from "./fonts.mjs";

const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const out = path.join(brand, "logo");
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });

fs.writeFileSync(path.join(out, "musebooks-mark.svg"), indexMark());
fs.writeFileSync(path.join(out, "musebooks-mark-on-dark.svg"), indexMark({ theme: "dark" }));

const { light: L, dark: D } = THEME;
const lockup = (theme, px) => `<div class="lock" style="font-size:${px}px;color:${THEME[theme].ink}">${indexMark({ theme })}<span>MuseBooks</span></div>`;
const css = `${fontCSS}
.lock{display:inline-flex;align-items:center;gap:.22em;font:800 1em/1 Hanken;letter-spacing:-.03em}
.lock svg{width:1.32em;height:1.32em;margin:-.06em -.12em 0 -.16em}
.app{border-radius:22.5%;display:grid;place-items:center}`;
const page = (body, bg, w, h) => `<!doctype html><meta charset="utf-8"><style>${css}body{margin:0;width:${w}px;height:${h}px;display:grid;place-items:center;background:${bg}}</style>${body}`;
const icon = (theme, s) => `<div class="app" style="width:${s}px;height:${s}px;background:${THEME[theme].bg};box-shadow:0 10px 26px rgba(0,0,0,.14)${theme === "light" ? ",inset 0 0 0 1px #e2e2df" : ""}">${indexMark({ theme, size: s * .74 })}</div>`;

const board = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;width:1600px;height:1000px;background:#e2e2df">
  <div style="background:${L.bg};display:grid;place-items:center">${lockup("light", 96)}</div>
  <div style="background:${D.bg};display:grid;place-items:center">${lockup("dark", 96)}</div>
  <div style="background:#f4f4f2;display:grid;place-items:center"><div style="display:flex;gap:26px;align-items:end">${icon("light", 200)}${icon("light", 110)}${icon("light", 60)}</div></div>
  <div style="background:#1a1a19;display:grid;place-items:center"><div style="display:flex;gap:26px;align-items:end">${icon("dark", 200)}${icon("dark", 110)}${icon("dark", 60)}<div style="display:flex;gap:14px;align-items:end;margin-left:20px">${[32, 16].map(s => indexMark({ theme: "dark", size: s })).join("")}</div></div></div>
</div>`;

const jobs = [
  ["musebooks-lockup.png", 1300, 320, "transparent", lockup("light", 150), 2],
  ["musebooks-lockup-on-dark.png", 1300, 320, "transparent", lockup("dark", 150), 2],
  ["musebooks-mark-1024.png", 1024, 1024, "transparent", indexMark({ size: 1024 }), 1],
  ["musebooks-mark-on-dark-1024.png", 1024, 1024, "transparent", indexMark({ theme: "dark", size: 1024 }), 1],
  ["app-icon-light-1024.png", 1024, 1024, L.bg, indexMark({ size: 760 }), 1],
  ["app-icon-dark-1024.png", 1024, 1024, D.bg, indexMark({ theme: "dark", size: 760 }), 1],
  ["favicon-32.png", 32, 32, "transparent", indexMark({ size: 32 }), 1],
  ["favicon-48.png", 48, 48, "transparent", indexMark({ size: 48 }), 1],
  ["musebooks-logo-board.png", 1600, 1000, "#fff", board, 1],
];

const browser = await chromium.launch();
for (const [name, w, h, bg, body, scale] of jobs) {
  const tab = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: scale });
  const file = path.join(brand, ".logo.html");
  fs.writeFileSync(file, page(body, bg, w, h));
  await tab.goto(pathToFileURL(file).href, { waitUntil: "networkidle" });
  await tab.evaluate(() => document.fonts.ready);
  await tab.screenshot({ path: path.join(out, name), omitBackground: bg === "transparent" });
  await tab.close();
}
fs.rmSync(path.join(brand, ".logo.html"));
await browser.close();
console.log(fs.readdirSync(out).join("\n"));
