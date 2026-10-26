// The MuseBooks mark, "Collector's Index": four catalog bars standing like
// spines on a shelf, the last one marked with a dot — the book you keep.
// Colours are the website/app tokens from frontend/src/styles.css.
export const THEME = {
  light: { ink: "#111111", accent: "#d0261b", bg: "#ffffff" },
  dark: { ink: "#f2f2ef", accent: "#ff5b4c", bg: "#0f0f0f" },
};

// Bars are 16 wide with 8 gaps; the outer bars stand taller than the inner pair.
const BARS = [[16, 60], [40, 44], [64, 44], [88, 60]];
const BASE = 99;

export function indexMark({ theme = "light", ink, accent, size, title = "MuseBooks" } = {}) {
  const t = THEME[theme];
  const fg = ink || t.ink, dot = accent || t.accent;
  const dims = size ? ` width="${size}" height="${size}"` : "";
  const bars = BARS.map(([x, h]) => `<rect x="${x}" y="${BASE - h}" width="16" height="${h}" rx="8"/>`).join("");
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"${dims} role="img" aria-label="${title}">
  <g fill="${fg}">${bars}</g>
  <circle cx="96" cy="27" r="6.5" fill="${dot}"/>
</svg>`;
}
