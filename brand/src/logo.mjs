// Logo deliverables only (no store art): node brand/src/logo.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { markSVG, onDark, LUXE } from "./mark.mjs";
import { luxeFontCSS } from "./fonts.mjs";

const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const out = path.join(brand, "logo");
fs.rmSync(out, { recursive: true, force: true });
fs.mkdirSync(out, { recursive: true });

fs.writeFileSync(path.join(out, "musebooks-mark.svg"), markSVG());
fs.writeFileSync(path.join(out, "musebooks-mark-on-dark.svg"), onDark());
fs.writeFileSync(path.join(out, "musebooks-mark-small.svg"), markSVG({ simple: true }));

const css = `${luxeFontCSS}
.wm{font:400 1em/1 Bodoni;letter-spacing:.22em;margin-right:-.22em}
.h{display:flex;align-items:center;gap:.32em}.h svg{width:2.3em;height:2.3em}
.v{display:grid;justify-items:center;gap:.35em}.v svg{width:3.6em;height:3.6em}
.rule{width:2.2em;height:1px;background:${LUXE.gold}}`;
const page = (body, bg, w, h) => `<!doctype html><meta charset="utf-8"><style>${css}body{margin:0;width:${w}px;height:${h}px;display:grid;place-items:center;background:${bg}}</style>${body}`;
const jobs = [
  ["musebooks-lockup.png", 1400, 300, "transparent", `<div class="h" style="font-size:72px;color:${LUXE.black}">${markSVG()}<span class="wm">MUSEBOOKS</span></div>`],
  ["musebooks-lockup-on-dark.png", 1400, 300, "transparent", `<div class="h" style="font-size:72px;color:${LUXE.ivory}">${onDark()}<span class="wm">MUSEBOOKS</span></div>`],
  ["musebooks-stacked.png", 900, 700, "transparent", `<div class="v" style="font-size:70px;color:${LUXE.black}">${markSVG()}<span class="wm">MUSEBOOKS</span></div>`],
  ["musebooks-stacked-on-dark.png", 900, 700, "transparent", `<div class="v" style="font-size:70px;color:${LUXE.ivory}">${onDark()}<span class="wm">MUSEBOOKS</span></div>`],
  ["musebooks-mark-1024.png", 1024, 1024, "transparent", markSVG({ size: 1024 })],
  ["musebooks-mark-on-dark-1024.png", 1024, 1024, "transparent", onDark({ size: 1024 })],
  ["app-icon-preview.png", 1024, 1024, LUXE.black, onDark({ size: 860 })],
];
// Presentation board for approval.
const sizes = [96, 64, 48, 32, 16];
jobs.push(["musebooks-logo-board.png", 1600, 1000, "#e9e6df", `<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;width:1600px;height:1000px;background:#d8d3c8">
  <div style="background:${LUXE.ivory};display:grid;place-items:center"><div class="v" style="font-size:44px;color:${LUXE.black}">${markSVG()}<span class="wm">MUSEBOOKS</span><span class="rule"></span><span style="font:400 15px Hanken;letter-spacing:.3em;color:#6b6457">PHOTOBOOK ARCHIVE</span></div></div>
  <div style="background:${LUXE.black};display:grid;place-items:center"><div class="v" style="font-size:44px;color:${LUXE.ivory}">${onDark()}<span class="wm">MUSEBOOKS</span><span class="rule"></span><span style="font:400 15px Hanken;letter-spacing:.3em;color:#a39d90">PHOTOBOOK ARCHIVE</span></div></div>
  <div style="background:#fff;display:grid;place-items:center;gap:30px"><div class="h" style="font-size:40px;color:${LUXE.black}">${markSVG()}<span class="wm">MUSEBOOKS</span></div><div style="display:flex;gap:18px;align-items:end">${sizes.map(s => markSVG({ size: s, simple: s <= 32 })).join("")}</div></div>
  <div style="background:#f0ede6;display:grid;place-items:center"><div style="display:flex;gap:28px;align-items:end">${[220, 120, 64].map(s => `<div style="width:${s}px;height:${s}px;border-radius:22.5%;background:${LUXE.black};display:grid;place-items:center;box-shadow:0 12px 30px rgba(0,0,0,.18)">${onDark({ size: s * .86, simple: s < 100 })}</div>`).join("")}</div></div>
</div>`]);

const browser = await chromium.launch();
for (const [name, w, h, bg, body] of jobs) {
  const tab = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: name.includes("lockup") || name.includes("stacked") ? 2 : 1 });
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
