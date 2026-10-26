// Round-two logo directions, rendered side by side for a decision.
// node brand/src/explore.mjs  ->  brand/explore/directions.png
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { fontCSS } from "./fonts.mjs";

const brand = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cells = list => list.map(([c, r, w = 1, h = 1]) => `<rect x="${c}" y="${r}" width="${w}" height="${h}"/>`).join("");

// A. Hanko: "MB" cut white into a vermilion seal, every stroke on a 9-cell grid.
const sealLetters = cells([
  [0, 1, 1, 7], [4, 1, 1, 7], [0, 1, 5, 1], [2, 1, 1, 5],          // M: squared seal-script form
  [6, 1, 1, 7], [6, 1, 3, 1], [8, 1, 1, 4], [6, 4, 4, 1], [9, 4, 1, 4], [6, 7, 4, 1], // B with open counters
]);
export function seal({ red = "#df3a1f", size, tilt = -3 } = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${size ? ` width="${size}" height="${size}"` : ""}>
  <defs><mask id="s" maskUnits="userSpaceOnUse" x="0" y="0" width="120" height="120">
    <rect width="120" height="120" fill="#fff"/>
    <g fill="#000" transform="translate(25 27) scale(7)">${sealLetters}</g>
    <path d="M14 30h3v6h-3z M103 86h3v5h-3z M38 103h7v3h-7z" fill="#000"/>
  </mask></defs>
  <g transform="rotate(${tilt} 60 60)"><rect x="14" y="14" width="92" height="92" rx="3" fill="${red}" mask="url(#s)"/></g>
</svg>`;
}

// B. Obi: a photobook jacket with its paper band — the strip every Japanese edition wears.
export function obi({ cover = "#14161f", band = "#f2d43a", ink = "#14161f", paper = "#fbfaf6", size } = {}) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${size ? ` width="${size}" height="${size}"` : ""}>
  <rect x="26" y="10" width="68" height="100" rx="2" fill="${cover}"/>
  <text x="60" y="66" text-anchor="middle" font-family="Gloock" font-size="62" fill="${paper}">M</text>
  <rect x="26" y="74" width="68" height="26" fill="${band}"/>
  <rect x="26" y="74" width="68" height="2.4" fill="${ink}" opacity=".18"/>
  <text x="60" y="91.5" text-anchor="middle" font-family="Azeret" font-weight="500" font-size="8.6" letter-spacing="1.6" fill="${ink}">BOOKS</text>
</svg>`;
}

// C. Contact sheet: three frames on a strip, one ringed in red grease pencil — the pick.
export function contact({ film = "#16140f", frame = "#3a352b", pencil = "#e2382a", size } = {}) {
  const holes = Array.from({ length: 9 }, (_, i) => `<rect x="${9 + i * 11.6}" y="31" width="5" height="4" rx="1"/><rect x="${9 + i * 11.6}" y="85" width="5" height="4" rx="1"/>`).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${size ? ` width="${size}" height="${size}"` : ""}>
  <defs><mask id="h" maskUnits="userSpaceOnUse" x="0" y="0" width="120" height="120"><rect width="120" height="120" fill="#fff"/><g fill="#000">${holes}</g></mask></defs>
  <rect x="4" y="27" width="112" height="66" rx="2" fill="${film}" mask="url(#h)"/>
  <rect x="8" y="40" width="30" height="40" fill="${frame}"/><rect x="82" y="40" width="30" height="40" fill="${frame}"/>
  <rect x="45" y="40" width="30" height="40" fill="#f3efe4"/>
  <text x="60" y="71" text-anchor="middle" font-family="Gloock" font-size="34" fill="${film}">M</text>
  <path d="M41 60c-2-17 12-26 25-24 13 2 19 12 17 25-2 14-16 22-30 19-11-2-17-10-15-19 1-4 3-7 6-9" fill="none" stroke="${pencil}" stroke-width="4" stroke-linecap="round"/>
</svg>`;
}

const directions = [
  ["A", "Publisher's seal", "Vermilion hanko on indigo. MB carved on a strict grid, stamped slightly off-square.", seal({}), "#1d2c4f", "#f6efe2", "#df3a1f", seal({ size: 34, tilt: 0 })],
  ["B", "Obi band", "Photobook jacket with its paper obi strip — the band every Japanese edition wears.", obi({}), "#f2d43a", "#14161f", "#14161f", obi({ size: 34 })],
  ["C", "Contact-sheet pick", "Three frames, one ringed in red grease pencil: the photobook worth keeping.", contact({}), "#ebe5d6", "#16140f", "#e2382a", contact({ size: 34 })],
];

const html = `<!doctype html><meta charset="utf-8"><style>${fontCSS}
body{width:1500px;background:#ddd;display:grid;grid-template-columns:repeat(3,1fr);gap:2px;font-family:Hanken}
section{display:grid;gap:22px;padding:32px;background:#fff;align-content:start}
h2{font:600 15px/1 Hanken;letter-spacing:.06em;text-transform:uppercase;color:#555}
h2 b{display:inline-grid;place-items:center;width:26px;height:26px;margin-right:8px;border-radius:50%;background:#111;color:#fff;font-size:13px}
.note{color:#555;font-size:14px;line-height:1.45;min-height:40px}
.icon{width:300px;height:300px;border-radius:66px;display:grid;place-items:center;justify-self:center;box-shadow:0 14px 30px rgba(0,0,0,.18)}
.icon svg{width:250px;height:250px}
.lock{display:flex;align-items:center;gap:10px;font:400 40px/1 Gloock;letter-spacing:-.02em;padding:18px 20px;border-radius:12px}
.lock svg{width:58px;height:58px}
.row{display:flex;gap:14px;align-items:center}
.phone{display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:10px;font:400 22px Gloock}
.tiny{display:flex;gap:12px;align-items:end}
.tiny div{border-radius:22%;display:grid;place-items:center}
</style>${directions.map(([k, name, note, svg, bg, fg, accent, small]) => `<section>
  <h2><b>${k}</b>${name}</h2><p class="note">${note}</p>
  <div class="icon" style="background:${bg}">${svg}</div>
  <div class="lock" style="background:#fff;color:#14161f">${svg}MuseBooks</div>
  <div class="lock" style="background:#111;color:#f2f2ef">${svg}MuseBooks</div>
  <div class="tiny">${[96, 64, 48, 32, 20].map(s => `<div style="width:${s}px;height:${s}px;background:${bg}">${svg.replace("<svg ", `<svg width="${s * .82}" height="${s * .82}" `)}</div>`).join("")}</div>
</section>`).join("")}`;
fs.mkdirSync(path.join(brand, "explore"), { recursive: true });
fs.writeFileSync(path.join(brand, "explore/directions.html"), html);
console.log("explore/directions.html");
