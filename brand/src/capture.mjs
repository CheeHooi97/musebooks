// Captures real app-shell screens (vite --mode mobile on :4174) for store art.
import { createRequire } from "node:module";
import fs from "node:fs";
const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const origin = "http://localhost:4174";
const out = new URL("../captures/", import.meta.url);
fs.mkdirSync(out, { recursive: true });

const books = await fetch(`${origin}/v1/books?pageSize=40`).then(r => r.json());
const saved = books.items.filter(b => b.publicationType !== "magazine_issue").slice(0, 3).map(b => b.id)
  .concat(["korea-maxim-2026-10-joo-digital", "korea-maxim-2026-04-kim-nayeon-digital"]);

const shots = [
  ["home", "/", 0],
  ["home-releases", "/", 560],
  ["browse", "/books", 0],
  ["book", "/books/korea-maxim-2026-10-joo-digital", 0],
  ["book-prices", "/books/korea-maxim-2026-10-joo-digital", "#available-editions"],
  ["models", "/models", 0],
  ["market", "/active", 0],
  ["saved", "/saved", 0],
];
const browser = await chromium.launch();
for (const theme of ["dark", "light"]) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, colorScheme: theme, isMobile: true, hasTouch: true });
  await ctx.addInitScript(([t, s]) => { localStorage.setItem("musebooks.theme.v1", t); localStorage.setItem("musebooks.collection.v1", JSON.stringify(s)); }, [theme, saved]);
  const page = await ctx.newPage();
  for (const [name, route, scroll] of shots) {
    page.setDefaultTimeout(90000); await page.goto(origin + route, { waitUntil: "networkidle" });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(800);
    await page.evaluate(target => {
      document.documentElement.style.scrollBehavior = "auto";
      const y = typeof target === "number" ? target : document.querySelector(target).getBoundingClientRect().top + scrollY - 70;
      window.scrollTo(0, y);
    }, scroll);
    await page.waitForTimeout(300);
    await page.screenshot({ path: new URL(`${name}-${theme}.png`, out).pathname.slice(1) });
    console.log(name, theme);
  }
  await ctx.close();
}
await browser.close();
