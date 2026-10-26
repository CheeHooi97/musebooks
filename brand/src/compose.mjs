// Builds the Google Play listing art from real app captures (logo files: logo-index.mjs).
// Run from the repo root after capture.mjs:  node brand/src/compose.mjs
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { indexMark, THEME } from "./index-mark.mjs";
import { fontCSS } from "./fonts.mjs";

const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const capture = name => pathToFileURL(path.join(brand, "captures", `${name}.png`)).href;

// Website/app palette (frontend/src/styles.css tokens).
const C = {
  ink: THEME.light.ink, paper: "#f4f4f2", red: THEME.light.accent, muted: "#5c5c5a",
  night: THEME.dark.bg, nightInk: THEME.dark.ink, nightRed: THEME.dark.accent, nightMuted: "#a9a9a4",
};
const dayMark = () => indexMark({ theme: "light" });
const nightMark = () => indexMark({ theme: "dark" });
const page = (body, css = "") => `<!doctype html><meta charset="utf-8"><style>${fontCSS}${css}</style>${body}`;

const lockupCSS = `.lockup{display:inline-flex;align-items:center;gap:.22em;font:800 1em/1 Hanken;letter-spacing:-.03em}
.lockup svg{width:1.32em;height:1.32em;margin:-.06em -.12em 0 -.16em}`;

// Phone frame: a plain bezel around the real capture (1170×2532 at 3×).
const phone = (shot, width, night = true) => `<div class="phone" style="width:${width}px">
  <img src="${capture(shot)}" alt=""></div>`;
const phoneCSS = `.phone{padding:14px;border-radius:64px;background:#1c1c1b;box-shadow:0 2px 0 1px #2b2b29 inset,0 40px 80px rgba(0,0,0,.45),0 8px 20px rgba(0,0,0,.3)}
.phone img{display:block;width:100%;border-radius:50px}`;

const screens = [
  ["phone-1-home", "home-releases-dark", true, "Find the next photobook <em>worth keeping</em>.", "Photobooks and magazine issues, every edition and its price."],
  ["phone-2-browse", "browse-dark", true, "Every verified publication, <em>one list</em>.", "Filter by origin, format and availability."],
  ["phone-3-editions", "book-prices-dark", true, "Every edition, <em>side by side</em>.", "Print, digital and subscriber editions with their recorded prices."],
  ["phone-4-models", "models-dark", true, "Follow the <em>models</em> you collect.", "Every credited model, idol and entertainer in one directory."],
  ["phone-5-market", "market-dark", true, "Prices with a <em>source</em>.", "Offers and sold records link back to where they were found."],
  ["phone-6-saved", "saved-light", false, "Your collection, <em>on your phone</em>.", "Save publications on this device — no account needed."],
];

const jobs = [];
const add = (out, w, h, html, { transparent = false, scale = 1 } = {}) => jobs.push({ out, w, h, html, transparent, scale });

for (const [out, shot, night, title, sub] of screens) {
  const bg = night ? C.night : C.paper, fg = night ? C.nightInk : C.ink, accent = night ? C.nightRed : C.red, muted = night ? C.nightMuted : C.muted;
  add(`google-play/${out}.png`, 1080, 1920, page(`
    <main>
      <header><span class="lockup">${(night ? nightMark : dayMark)()}MuseBooks</span></header>
      <h1>${title}</h1>
      <p>${sub}</p>
      <div class="device">${phone(shot, 660, night)}</div>
    </main>`, `${lockupCSS}${phoneCSS}
    body{width:1080px;height:1920px;overflow:hidden;background:${bg};color:${fg}}
    main{position:relative;height:100%;padding:84px 88px 0;background:radial-gradient(120% 60% at 50% 100%, ${night ? "#232322" : "#e6e6e2"} 0%, transparent 70%)}
    header{font-size:40px;margin-bottom:56px}
    h1{font:400 84px/1.04 Gloock;letter-spacing:-.025em;text-wrap:balance;max-width:900px}
    h1 em{font-style:normal;color:${accent}}
    p{margin-top:24px;font:400 32px/1.35 Hanken;color:${muted};max-width:860px;text-wrap:pretty}
    .device{position:absolute;left:50%;bottom:-120px;transform:translateX(-50%)}`));
}

// Feature graphic: brand left, two real screens right.
add("google-play/feature-graphic-1024x500.png", 1024, 500, page(`
  <main>
    <div class="copy">
      <span class="lockup">${nightMark()}MuseBooks</span>
      <h1>Find the next photobook <em>worth keeping</em>.</h1>
      <p>Every edition and its source-backed price, for photobooks and magazine issues.</p>
    </div>
    <div class="back">${phone("book-prices-dark", 230)}</div>
    <div class="front">${phone("home-releases-dark", 250)}</div>
  </main>`, `${lockupCSS}${phoneCSS}
  body{width:1024px;height:500px;overflow:hidden;background:${C.night};color:${C.nightInk}}
  main{position:relative;height:100%;background:radial-gradient(70% 90% at 82% 100%, #262624 0%, transparent 70%)}
  .copy{position:absolute;left:64px;top:62px;width:500px}
  .lockup{font-size:34px}
  h1{margin-top:44px;font:400 54px/1.04 Gloock;letter-spacing:-.025em;text-wrap:balance}
  h1 em{font-style:normal;color:${C.nightRed}}
  p{margin-top:20px;font:400 19px/1.45 Hanken;color:${C.nightMuted};max-width:430px}
  .phone{padding:8px;border-radius:36px}.phone img{border-radius:29px}
  .back{position:absolute;left:640px;top:70px;transform:rotate(-5deg);opacity:.9}
  .front{position:absolute;left:790px;top:118px;transform:rotate(4deg)}`));

// Google Play icon: full-bleed square; Play applies its own corner mask.
add("google-play/icon-512.png", 512, 512, page(`<div>${nightMark()}</div>`,
  `body{width:512px;height:512px;background:${C.night};display:grid;place-items:center}div svg{width:380px;height:380px;display:block}`), { transparent: true });

const browser = await chromium.launch();
for (const job of jobs) {
  const tab = await browser.newPage({ viewport: { width: job.w, height: job.h }, deviceScaleFactor: job.scale });
  const file = path.join(brand, ".render.html");
  fs.writeFileSync(file, job.html);
  await tab.goto(pathToFileURL(file).href, { waitUntil: "networkidle" });
  await tab.evaluate(() => document.fonts.ready);
  fs.mkdirSync(path.dirname(path.join(brand, job.out)), { recursive: true });
  await tab.screenshot({ path: path.join(brand, job.out), omitBackground: job.transparent });
  await tab.close();
  console.log(job.out);
}
fs.rmSync(path.join(brand, ".render.html"));
await import("node:child_process").then(({ execFileSync }) => execFileSync(process.execPath, [path.join(brand, "src/rgba-png.mjs"), path.join(brand, "google-play/icon-512.png")], { stdio: "inherit" }));
await browser.close();
