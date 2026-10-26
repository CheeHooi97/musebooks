// Pictorial photobook marks, round three. node brand/src/photobook.mjs -> brand/explore/photobook.png
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fontCSS } from "./fonts.mjs";
import { MUSE } from "./muse.mjs";

const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
export const P = { indigo: "#1b2a4a", vermilion: "#df3a1f", paper: "#f6f0e4", shade: "#d9cfbc" };

// A muse in profile, facing the gutter: hair gathered in a bun, brow, nose, lips, chin, neck.
const profile = (x, y, s) => `<path transform="translate(${x} ${y}) scale(${s})" d="${MUSE}"/>`;

// 1. Open spread: caption page on the left, a full-bleed portrait on the right.
export function spread({ size, ink = P.indigo, page = P.paper, photo = P.vermilion, edge = P.shade } = {}) {
  return svg(size, `
  <path d="M60 32 C48 26 30 24 12 27 V93 C30 90 48 92 60 98 Z" fill="${page}"/>
  <path d="M60 32 C72 26 90 24 108 27 V93 C90 90 72 92 60 98 Z" fill="${page}"/>
  <path d="M12 93 C30 90 48 92 60 98 C72 92 90 90 108 93 V97 C90 94 72 96 60 102 C48 96 30 94 12 97 Z" fill="${edge}"/>
  <clipPath id="sp"><path d="M63 33.5 C74 28.5 89 27 104 29.4 V89.5 C89 87.5 74 89 63 94 Z"/></clipPath>
  <g clip-path="url(#sp)"><rect x="60" y="20" width="50" height="80" fill="${photo}"/><g fill="${ink}">${profile(66, 36, 0.62)}</g></g>
  <g fill="${ink}" opacity=".55"><rect x="20" y="70" width="26" height="2.4" rx="1.2"/><rect x="20" y="76" width="17" height="2.4" rx="1.2"/></g>`);
}

// 2. Closed photobook: full-bleed portrait cover, page block on the fore-edge, paper obi.
export function cover({ size, ink = P.indigo, page = P.paper, photo = P.vermilion, edge = P.shade } = {}) {
  return svg(size, `
  <path d="M86 18 L94 22 V104 L86 102 Z" fill="${edge}"/>
  <rect x="28" y="16" width="58" height="86" rx="2" fill="${photo}"/>
  <clipPath id="cv"><rect x="28" y="16" width="58" height="86" rx="2"/></clipPath>
  <g clip-path="url(#cv)" fill="${ink}">${profile(30, 22, 0.86)}</g>
  <rect x="28" y="80" width="58" height="16" fill="${page}"/>
  <rect x="35" y="86.5" width="30" height="3" rx="1.5" fill="${ink}"/>`);
}

// 3. Open spread, landscape: a sun over a horizon framed in viewfinder corners.
export function viewfinder({ size, ink = P.indigo, page = P.paper, photo = P.vermilion, edge = P.shade } = {}) {
  const c = (x, y, dx, dy) => `<path d="M${x} ${y + dy * 7} V${y} H${x + dx * 7}" fill="none" stroke="${ink}" stroke-width="2.6"/>`;
  return svg(size, `
  <path d="M60 32 C48 26 30 24 12 27 V93 C30 90 48 92 60 98 Z" fill="${page}"/>
  <path d="M60 32 C72 26 90 24 108 27 V93 C90 90 72 92 60 98 Z" fill="${page}"/>
  <path d="M12 93 C30 90 48 92 60 98 C72 92 90 90 108 93 V97 C90 94 72 96 60 102 C48 96 30 94 12 97 Z" fill="${edge}"/>
  <circle cx="60" cy="58" r="15" fill="${photo}"/>
  <path d="M24 82 C36 66 46 72 60 62 C74 72 84 64 96 80 C84 84 72 82 60 88 C48 82 36 84 24 82 Z" fill="${ink}"/>
  ${c(20, 38, 1, 1)}${c(100, 38, -1, 1)}`);
}

function svg(size, body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${size ? ` width="${size}" height="${size}"` : ""}>${body}</svg>`;
}

const variants = [["1", "Open spread · portrait", spread], ["2", "Cover · portrait + obi", cover], ["3", "Open spread · viewfinder", viewfinder]];
const html = `<!doctype html><meta charset="utf-8"><style>${fontCSS}
body{width:1500px;background:#ddd;display:grid;grid-template-columns:repeat(3,1fr);gap:2px;font-family:Hanken}
section{display:grid;gap:20px;padding:30px;background:#fff;align-content:start}
h2{font:600 15px Hanken;letter-spacing:.06em;text-transform:uppercase;color:#555}
.icon{width:300px;height:300px;border-radius:66px;background:${P.indigo};display:grid;place-items:center;justify-self:center}
.icon svg{width:270px;height:270px}
.lock{display:flex;align-items:center;gap:8px;font:400 40px/1 Gloock;letter-spacing:-.02em;padding:14px 18px;border-radius:12px}
.lock svg{width:64px;height:64px}
.tiny{display:flex;gap:12px;align-items:end}.tiny div{border-radius:22%;background:${P.indigo};display:grid;place-items:center}
</style>${variants.map(([k, name, fn]) => `<section><h2>${k} · ${name}</h2>
<div class="icon">${fn({})}</div>
<div class="lock" style="color:${P.indigo}">${fn({ page: "#efe6d4" })}MuseBooks</div>
<div class="lock" style="background:#111;color:${P.paper}">${fn({})}MuseBooks</div>
<div class="tiny">${[96, 64, 48, 32, 20].map(s => `<div style="width:${s}px;height:${s}px">${fn({ size: s * .9 })}</div>`).join("")}</div></section>`).join("")}`;
fs.mkdirSync(path.join(brand, "explore"), { recursive: true });
fs.writeFileSync(path.join(brand, "explore/photobook.html"), html);
