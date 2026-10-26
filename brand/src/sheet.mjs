import fs from "node:fs";
import { markSVG } from "./mark.mjs";
import { fontCSS } from "./fonts.mjs";
const dark = { ink: "#f2f2ef", accent: "#ff5b4c", paper: "#111111" };
fs.writeFileSync(new URL("../out-sheet.html", import.meta.url), `<!doctype html><meta charset="utf-8"><style>${fontCSS}
body{display:grid;grid-template-columns:1fr 1fr;width:1200px;font-family:Hanken}
section{display:grid;place-items:center;gap:28px;padding:48px}
.p{background:#f4f1ea;color:#111}.d{background:#111;color:#f2f2ef}
.lock{display:flex;align-items:center;gap:18px;font:400 64px/1 Gloock;letter-spacing:-.02em}
.sizes{display:flex;align-items:end;gap:24px}
</style>
<section class="p">${markSVG({ size: 320 })}<div class="lock">${markSVG({ size: 76 })}MuseBooks</div><div class="sizes">${[96,48,32,16].map(s=>markSVG({size:s})).join("")}</div></section>
<section class="d">${markSVG({ size: 320, ...dark })}<div class="lock">${markSVG({ size: 76, ...dark })}MuseBooks</div><div class="sizes">${[96,48,32,16].map(s=>markSVG({size:s,...dark})).join("")}</div></section>`);
