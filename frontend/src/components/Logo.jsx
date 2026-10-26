// The MuseBooks mark: four catalog bars, the last one marked with the accent dot.
// Bars follow the text colour and the dot the theme accent, so it adapts to light and dark.
export function LogoMark({ size = 28, className = "logo-mark" }) {
  return <svg className={className} width={size} height={size} viewBox="0 0 120 120" aria-hidden="true" focusable="false">
    <g fill="currentColor">
      <rect x="16" y="39" width="16" height="60" rx="8" />
      <rect x="40" y="55" width="16" height="44" rx="8" />
      <rect x="64" y="55" width="16" height="44" rx="8" />
      <rect x="88" y="39" width="16" height="60" rx="8" />
    </g>
    <circle cx="96" cy="27" r="6.5" fill="var(--accent)" />
  </svg>;
}

export default function Logo() {
  return <><LogoMark /><span>MuseBooks</span></>;
}
