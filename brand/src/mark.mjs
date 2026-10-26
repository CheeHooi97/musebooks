// The MuseBooks mark: a photobook in the manner of an art-photography imprint.
// A black cover holds an ivory cameo of the muse; a champagne-gold obi wraps
// its foot; hairlines on the fore-edge and tail show the thick page block.
// Swap cover and cameo for dark grounds (ivory book, black muse).
import { MUSE } from "./muse.mjs";

export const LUXE = { black: "#0c0c0c", ivory: "#f5f1e8", gold: "#b89a5e" };

let uid = 0;
export function markSVG({ cover = LUXE.black, cameo = LUXE.ivory, gold = LUXE.gold, line, size, simple = false, title = "MuseBooks" } = {}) {
  const id = `mb${++uid}`;
  const edge = line || cover;
  const dims = size ? ` width="${size}" height="${size}"` : "";
  const hair = simple ? 2.2 : 1.3;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${dims} role="img" aria-label="${title}">
  <defs><clipPath id="${id}"><rect x="31" y="14" width="56" height="65"/></clipPath></defs>
  <path d="M87 15.5 L93 19 V106 L87 104" fill="none" stroke="${edge}" stroke-width="${hair}" stroke-linejoin="round"/>
  ${simple ? "" : `<path d="M31 104 L37 107.5 H93" fill="none" stroke="${edge}" stroke-width="${hair * .7}"/>`}
  <rect x="31" y="14" width="56" height="90" fill="${cover}"/>
  <g clip-path="url(#${id})"><path transform="translate(34 21) scale(.82)" d="${MUSE}" fill="${cameo}"/></g>
  <rect x="31" y="79" width="56" height="12" fill="${gold}"/>
  ${simple ? "" : `<rect x="39" y="84.6" width="26" height=".9" fill="${cover}"/>`}
</svg>`;
}
export const onDark = o => markSVG({ cover: LUXE.ivory, cameo: LUXE.black, ...o });
