// Draws the MuseBooks app icon (resources/icon-only.png, same geometry as
// public/favicon.svg) as PWA PNGs without an image library. The bars sit inside
// the maskable safe zone, so one drawing serves both "any" and "maskable".
// Run: node scripts/make-pwa-icons.mjs
import fs from 'node:fs'
import path from 'node:path'
import zlib from 'node:zlib'
import { fileURLToPath } from 'node:url'

const BACKGROUND = [15, 15, 15], BAR = [242, 242, 239], DOT = [255, 91, 76]
// favicon.svg units (viewBox 0 0 120 120), placed as in the 1024px app icon.
const BARS = [[16, 39, 60], [40, 55, 44], [64, 55, 44], [88, 39, 60]]
const SCALE = 6.32 / 1024, OFFSET = 132 / 1024, SAMPLES = 4

function inBar(x, y) {
  for (const [left, top, height] of BARS) {
    const right = left + 16, bottom = top + height, r = 8
    if (x < left || x > right || y < top || y > bottom) continue
    const cy = Math.min(Math.max(y, top + r), bottom - r)
    if ((x - (left + r)) ** 2 + (y - cy) ** 2 <= r * r) return true
  }
  return false
}

function pixels(size) {
  const data = Buffer.alloc(size * (size * 3 + 1))
  for (let py = 0; py < size; py++) {
    data[py * (size * 3 + 1)] = 0 // PNG filter: none
    for (let px = 0; px < size; px++) {
      const sum = [0, 0, 0]
      for (let sy = 0; sy < SAMPLES; sy++) for (let sx = 0; sx < SAMPLES; sx++) {
        const x = ((px + (sx + 0.5) / SAMPLES) / size - OFFSET) / SCALE
        const y = ((py + (sy + 0.5) / SAMPLES) / size - OFFSET) / SCALE
        const color = (x - 96) ** 2 + (y - 27) ** 2 <= 6.5 ** 2 ? DOT : inBar(x, y) ? BAR : BACKGROUND
        for (let i = 0; i < 3; i++) sum[i] += color[i]
      }
      for (let i = 0; i < 3; i++) data[py * (size * 3 + 1) + 1 + px * 3 + i] = Math.round(sum[i] / SAMPLES ** 2)
    }
  }
  return data
}

const CRC = Array.from({ length: 256 }, (_, n) => { for (let k = 0; k < 8; k++) n = n & 1 ? 0xedb88320 ^ (n >>> 1) : n >>> 1; return n >>> 0 })
const crc32 = buffer => { let c = 0xffffffff; for (const byte of buffer) c = CRC[(c ^ byte) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0 }
function chunk(type, body) {
  const out = Buffer.alloc(12 + body.length)
  out.writeUInt32BE(body.length, 0)
  out.write(type, 4, 'ascii')
  body.copy(out, 8)
  out.writeUInt32BE(crc32(out.subarray(4, 8 + body.length)), 8 + body.length)
  return out
}
export function iconPNG(size) {
  const header = Buffer.alloc(13)
  header.writeUInt32BE(size, 0)
  header.writeUInt32BE(size, 4)
  header.set([8, 2, 0, 0, 0], 8) // 8-bit RGB
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', header), chunk('IDAT', zlib.deflateSync(pixels(size), { level: 9 })), chunk('IEND', Buffer.alloc(0))])
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const publicDir = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public')
  for (const [name, size] of [['icon-192.png', 192], ['icon-512.png', 512]]) {
    fs.writeFileSync(path.join(publicDir, name), iconPNG(size))
    console.log(`wrote public/${name}`)
  }
}
