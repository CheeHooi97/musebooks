// Five luxury editorial photobook marks for a decision. node brand/src/luxe-set.mjs
// Every mark takes { fg, bg } so it can be drawn for light (black on ivory)
// and dark (ivory on black) grounds; gold is the single accent.
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { luxeFontCSS } from "./fonts.mjs";
import { MUSE } from "./muse.mjs";
import { markSVG as cameoCover, LUXE } from "./mark.mjs";

const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const { black, ivory, gold } = LUXE;
let uid = 0;
const svg = (size, body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${size ? ` width="${size}" height="${size}"` : ""}>${body}</svg>`;
const muse = (x, y, s, fill, clip) => `<g clip-path="url(#${clip})"><path transform="translate(${x} ${y}) scale(${s})" d="${MUSE}" fill="${fill}"/></g>`;

// 1. Cameo cover — the current proposal.
const cover = ({ fg, bg, size, small }) => cameoCover({ cover: fg, cameo: bg, size, simple: small });

// 2. Die-cut cover — an oval window cut through the jacket reveals the muse; gold-foil title.
function diecut({ fg, bg, size, small }) {
  const id = `d${++uid}`;
  return svg(size, `<defs><clipPath id="${id}"><ellipse cx="59" cy="50" rx="17" ry="22.5"/></clipPath></defs>
  <path d="M87 15.5 L93 19 V106 L87 104" fill="none" stroke="${fg}" stroke-width="${small ? 2.2 : 1.3}"/>
  <rect x="31" y="14" width="56" height="90" fill="${fg}"/>
  <ellipse cx="59" cy="50" rx="17" ry="22.5" fill="${bg}"/>
  ${muse(45, 32, .5, fg, id)}
  <ellipse cx="59" cy="50" rx="19.5" ry="25" fill="none" stroke="${gold}" stroke-width="${small ? 2 : 1}"/>
  <rect x="43" y="84" width="32" height="${small ? 3 : 1.6}" fill="${gold}"/>
  ${small ? "" : `<rect x="50" y="89.5" width="18" height="1" fill="${gold}"/>`}`);
}

// 3. Open spread — caption page and a full-bleed portrait plate, gold ribbon in the gutter.
function spread({ fg, bg, size, small }) {
  const id = `s${++uid}`;
  const w = small ? 2.4 : 1.4;
  return svg(size, `<defs><clipPath id="${id}"><rect x="64" y="33" width="36" height="52"/></clipPath></defs>
  <path d="M60 30 C48 25 30 24 12 26 V92 C30 90 48 91 60 96 C72 91 90 90 108 92 V26 C90 24 72 25 60 30 Z M60 30 V96" fill="none" stroke="${fg}" stroke-width="${w}" stroke-linejoin="round"/>
  <rect x="64" y="33" width="36" height="52" fill="${fg}"/>
  ${muse(67, 40, .53, bg, id)}
  ${small ? "" : `<g fill="${fg}"><rect x="21" y="72" width="27" height="1.2"/><rect x="21" y="77" width="17" height="1.2"/></g>`}
  <path d="M58 95.4 V110 L60.5 107 L63 110 V95.4" fill="${gold}"/>`);
}

// 4. Album print — a portrait print held on the page by four gold photo corners.
function corners({ fg, bg, size, small }) {
  const id = `a${++uid}`;
  const c = (x, y, dx, dy) => `<path d="M${x} ${y} h${dx * 15} L${x} ${y + dy * 15} Z" fill="${gold}"/>`;
  return svg(size, `<defs><clipPath id="${id}"><rect x="32" y="18" width="56" height="78"/></clipPath></defs>
  <rect x="32" y="18" width="56" height="78" fill="${fg}"/>
  ${muse(36, 26, .82, bg, id)}
  ${c(28, 14, 1, 1)}${c(92, 14, -1, 1)}${c(28, 100, 1, -1)}${c(92, 100, -1, -1)}
  ${small ? "" : `<rect x="40" y="106" width="40" height="1" fill="${fg}" opacity=".55"/>`}`);
}

// 5. Arched plate — the muse in a gallery arch, double gold rule, ribbon marker below.
function arch({ fg, bg, size, small }) {
  const id = `r${++uid}`;
  const a = "M34 100 V50 A26 26 0 0 1 86 50 V100 Z";
  return svg(size, `<defs><clipPath id="${id}"><path d="${a}"/></clipPath></defs>
  <path d="M29 105 V50 A31 31 0 0 1 91 50 V105 Z" fill="none" stroke="${gold}" stroke-width="${small ? 2.2 : 1.2}"/>
  <path d="${a}" fill="${fg}"/>
  ${muse(37, 30, .86, bg, id)}
  <path d="M56 100 V113 L60 109.5 L64 113 V100" fill="${gold}"/>`);
}

const designs = [
  ["1", "Cameo cover", "A black photobook with an ivory cameo of the muse and a gold obi.", cover],
  ["2", "Die-cut cover", "An oval window cut through the jacket reveals the muse; gold foil title.", diecut],
  ["3", "Open spread", "Caption page and a full-bleed portrait plate, gold ribbon in the gutter.", spread],
  ["4", "Album print", "A portrait print mounted on the page by four gold photo corners.", corners],
  ["5", "Arched plate", "The muse in a gallery arch with a gold rule and ribbon marker.", arch],
];

const html = `<!doctype html><meta charset="utf-8"><style>${luxeFontCSS}
body{margin:0;width:2000px;display:grid;grid-template-columns:repeat(5,1fr);gap:2px;background:#d8d3c8}
section{display:grid;grid-template-rows:auto 330px 250px auto;background:${ivory}}
header{padding:26px 26px 0;font-family:Hanken}
header b{display:block;font:400 30px/1 Bodoni;letter-spacing:.04em;color:${black}}
header b i{font-style:normal;color:${gold};margin-right:10px}
header p{margin-top:10px;color:#6b6457;font-size:14px;line-height:1.45;min-height:40px}
.light{display:grid;place-items:center;align-content:center;gap:16px;color:${black}}
.light svg{width:170px;height:170px}
.wm{font:400 25px/1 Bodoni;letter-spacing:.24em;margin-right:-.24em}
.dark{background:${black};display:grid;place-items:center;align-content:center;gap:14px;color:${ivory}}
.dark svg{width:130px;height:130px}
.foot{display:flex;gap:14px;align-items:end;justify-content:center;padding:22px;background:#fff}
.app{border-radius:22.5%;background:${black};display:grid;place-items:center}
</style>${designs.map(([n, name, note, fn]) => `<section>
  <header><b><i>${n}</i>${name}</b><p>${note}</p></header>
  <div class="light">${fn({ fg: black, bg: ivory })}<span class="wm">MUSEBOOKS</span></div>
  <div class="dark">${fn({ fg: ivory, bg: black })}<span class="wm">MUSEBOOKS</span></div>
  <div class="foot">${[110, 64, 40].map(s => `<div class="app" style="width:${s}px;height:${s}px">${fn({ fg: ivory, bg: black, size: s * .88, small: s < 80 })}</div>`).join("")}${[32, 16].map(s => fn({ fg: black, bg: ivory, size: s, small: true })).join("")}</div>
</section>`).join("")}`;

const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const file = path.join(brand, "explore/luxe-set.html");
fs.mkdirSync(path.dirname(file), { recursive: true });
fs.writeFileSync(file, html);
const browser = await chromium.launch();
const tab = await browser.newPage({ viewport: { width: 2000, height: 820 } });
await tab.goto(pathToFileURL(file).href, { waitUntil: "networkidle" });
await tab.evaluate(() => document.fonts.ready);
await tab.screenshot({ path: path.join(brand, "explore/musebooks-logo-options.png"), fullPage: true });
await browser.close();
fs.rmSync(file);
console.log("explore/musebooks-logo-options.png");
