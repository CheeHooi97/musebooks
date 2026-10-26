// Re-encodes a PNG as 32-bit RGBA (Google Play requires an alpha channel on the
// app icon; Chromium writes opaque screenshots as 24-bit RGB). Usage: node rgba-png.mjs <file.png>
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
const require = createRequire("D:/Workspace/Go/gravure-model/frontend/package.json");
const { chromium } = require("playwright");
const file = path.resolve(process.argv[2]);
const browser = await chromium.launch();
const page = await browser.newPage();
const { width, height, data } = await page.evaluate(async src => {
  const img = new Image(); img.src = src; await img.decode();
  const c = Object.assign(document.createElement("canvas"), { width: img.width, height: img.height });
  const ctx = c.getContext("2d"); ctx.drawImage(img, 0, 0);
  return { width: c.width, height: c.height, data: Array.from(ctx.getImageData(0, 0, c.width, c.height).data) };
}, `data:image/png;base64,${fs.readFileSync(file).toString("base64")}`);
await browser.close();

const table = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
const crc = buf => { let c = 0xffffffff; for (const b of buf) c = table[(c ^ b) & 0xff] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
const chunk = (type, body) => { const len = Buffer.alloc(4); len.writeUInt32BE(body.length); const td = Buffer.concat([Buffer.from(type), body]); const sum = Buffer.alloc(4); sum.writeUInt32BE(crc(td)); return Buffer.concat([len, td, sum]); };
const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(width, 0); ihdr.writeUInt32BE(height, 4); ihdr[8] = 8; ihdr[9] = 6;
const raw = Buffer.alloc(height * (width * 4 + 1));
for (let y = 0; y < height; y++) Buffer.from(data.slice(y * width * 4, (y + 1) * width * 4)).copy(raw, y * (width * 4 + 1) + 1);
fs.writeFileSync(file, Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk("IHDR", ihdr), chunk("IDAT", zlib.deflateSync(raw, { level: 9 })), chunk("IEND", Buffer.alloc(0))]));
console.log(path.basename(file), `${width}x${height}`, "RGBA");
