// Round four: the photobook mark as a luxury editorial imprint.
// Black and ivory, one champagne-gold accent, hairline drawing.
// node brand/src/luxe.mjs -> brand/explore/luxe.png
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { luxeFontCSS } from "./fonts.mjs";
import { MUSE } from "./muse.mjs";

const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const LUXE = { black: "#0c0c0c", ivory: "#f5f1e8", gold: "#b89a5e" };

let uid = 0;
const svg = (size, body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${size ? ` width="${size}" height="${size}"` : ""}>${body}</svg>`;

// A. Hairline photobook: outlined cover, the muse drawn as a single contour, gold obi rule.
export function hairline({ size, ink = LUXE.black, gold = LUXE.gold, w = 1.6 } = {}) {
  const id = `h${++uid}`;
  return svg(size, `<defs><clipPath id="${id}"><rect x="30" y="16" width="56" height="62"/></clipPath></defs>
  <rect x="30" y="16" width="56" height="88" fill="none" stroke="${ink}" stroke-width="${w}"/>
  <path d="M86 16 L92 19.5 V107 L86 104" fill="none" stroke="${ink}" stroke-width="${w}"/>
  <path d="M30 104 L36 107.5 H92" fill="none" stroke="${ink}" stroke-width="${w * .6}"/>
  <g clip-path="url(#${id})"><path transform="translate(33 24) scale(.82)" d="${MUSE}" fill="none" stroke="${ink}" stroke-width="${w / .82}" stroke-linejoin="round"/></g>
  <rect x="30" y="78" width="56" height="12" fill="${gold}"/>`);
}

// B. Solid portrait: black cover holding an ivory cameo of the muse, gold obi.
export function cameo({ size, ink = LUXE.black, ivory = LUXE.ivory, gold = LUXE.gold, edge } = {}) {
  const id = `c${++uid}`;
  return svg(size, `<defs><clipPath id="${id}"><rect x="30" y="16" width="56" height="88"/></clipPath></defs>
  <path d="M86 18 L92 21.5 V106 L86 104" fill="none" stroke="${edge || ink}" stroke-width="1.4"/>
  <rect x="30" y="16" width="56" height="88" fill="${ink}"/>
  <g clip-path="url(#${id})"><path transform="translate(33 24) scale(.82)" d="${MUSE}" fill="${ivory}"/>
  <rect x="30" y="80" width="56" height="10" fill="${gold}"/></g>`);
}

// C. Open spread in hairline: caption rules left, portrait plate right, gold ribbon.
export function spread({ size, ink = LUXE.black, gold = LUXE.gold, w = 1.5 } = {}) {
  const id = `s${++uid}`;
  return svg(size, `<defs><clipPath id="${id}"><rect x="65" y="34" width="34" height="50"/></clipPath></defs>
  <path d="M60 30 C48 25 30 24 12 26 V92 C30 90 48 91 60 96 C72 91 90 90 108 92 V26 C90 24 72 25 60 30 Z M60 30 V96" fill="none" stroke="${ink}" stroke-width="${w}" stroke-linejoin="round"/>
  <rect x="65" y="34" width="34" height="50" fill="${ink}"/>
  <g clip-path="url(#${id})"><path transform="translate(67 41) scale(.5)" d="${MUSE}" fill="${LUXE.ivory}"/></g>
  <g fill="${ink}"><rect x="21" y="70" width="26" height="${w}"/><rect x="21" y="75" width="16" height="${w}"/></g>
  <path d="M60 96 V108 L62.5 105 L65 108 V94.5" fill="${gold}"/>`);
}

const wordmark = color => `<span class="wm" style="color:${color}">MUSEBOOKS</span>`;
const rows = [["A", "Hairline photobook", hairline], ["B", "Cameo cover", cameo], ["C", "Open spread", spread]];
const html = `<!doctype html><meta charset="utf-8"><style>${luxeFontCSS}
body{width:1500px;display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:#ccc}
section{display:grid;gap:18px;padding:28px;background:#fff;align-content:start}
h2{font:600 14px Hanken;letter-spacing:.08em;text-transform:uppercase;color:#666}
.icon{width:280px;height:280px;border-radius:62px;display:grid;place-items:center;justify-self:center}
.icon svg{width:240px;height:240px}
.lock{display:flex;align-items:center;gap:14px;padding:18px 20px}
.lock svg{width:70px;height:70px}
.wm{font:400 33px/1 Bodoni;letter-spacing:.2em}
.stack{display:grid;justify-items:center;gap:10px;padding:22px}
.stack svg{width:110px;height:110px}.stack .wm{font-size:28px}
.tiny{display:flex;gap:12px;align-items:end}
</style>${rows.map(([k, name, fn]) => `<section><h2>${k} · ${name}</h2>
<div class="icon" style="background:${LUXE.black}">${fn({ ink: LUXE.ivory, ivory: LUXE.black })}</div>
<div class="lock">${fn({})}${wordmark(LUXE.black)}</div>
<div class="lock" style="background:${LUXE.black}">${fn({ ink: LUXE.ivory, ivory: LUXE.black })}${wordmark(LUXE.ivory)}</div>
<div class="tiny">${[64, 48, 32, 20].map(s => `<div style="width:${s}px;height:${s}px;border-radius:22%;background:${LUXE.black};display:grid;place-items:center">${fn({ size: s * .9, ink: LUXE.ivory, ivory: LUXE.black, w: 2.4 })}</div>`).join("")}${[32, 16].map(s => fn({ size: s, w: 2.6 })).join("")}</div>
</section>`).join("")}`;
fs.mkdirSync(path.join(brand, "explore"), { recursive: true });
fs.writeFileSync(path.join(brand, "explore/luxe.html"), html);
