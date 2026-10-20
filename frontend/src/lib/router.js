import { useSyncExternalStore } from "react";

// A small history router. Internal <a href> links are intercepted so pages
// change without a reload; every route still has a real URL for SEO and sharing.
const listeners = new Set();
const backHandlers = [];
let snapshot = readLocation();

function readLocation() {
  return { pathname: window.location.pathname.replace(/\/+$/, "") || "/", search: window.location.search, hash: window.location.hash };
}
function emit() {
  snapshot = readLocation();
  listeners.forEach(listener => listener());
}
function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
window.addEventListener("popstate", emit);

export function useLocation() {
  return useSyncExternalStore(subscribe, () => snapshot);
}

export function navigate(to, { replace = false, scroll = true } = {}) {
  const url = new URL(to, window.location.href);
  if (url.origin !== window.location.origin) { window.location.assign(url.href); return; }
  const next = `${url.pathname}${url.search}${url.hash}`;
  if (next !== `${window.location.pathname}${window.location.search}${window.location.hash}`) window.history[replace ? "replaceState" : "pushState"](null, "", next);
  emit();
  if (!scroll) return;
  if (url.hash) requestAnimationFrame(() => document.getElementById(decodeURIComponent(url.hash.slice(1)))?.scrollIntoView());
  else window.scrollTo(0, 0);
}

/** Replace only the query string, e.g. when filters change. */
export function setSearchParams(params) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) if (value) search.set(key, value);
  const query = search.toString();
  navigate(`${window.location.pathname}${query ? `?${query}` : ""}`, { replace: true, scroll: false });
}

export function interceptLinks(event) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const link = event.target instanceof Element ? event.target.closest("a[href]") : null;
  if (!link || link.target || link.hasAttribute("download") || link.hasAttribute("data-external-link") || link.dataset.reload !== undefined) return;
  const url = new URL(link.href, window.location.href);
  if (url.origin !== window.location.origin || /\.(md|txt|xml|json)$/.test(url.pathname)) return;
  // Same-page anchors keep the browser's own scrolling behaviour.
  if (url.pathname === window.location.pathname && url.search === window.location.search && url.hash) return;
  event.preventDefault();
  navigate(url.href);
}

/** Overlays (filter sheets, menus) register here so the Android back button closes them first. */
export function pushBackHandler(handler) {
  backHandlers.push(handler);
  return () => { const index = backHandlers.lastIndexOf(handler); if (index >= 0) backHandlers.splice(index, 1); };
}
export function runBackHandler() {
  const handler = backHandlers.at(-1);
  if (!handler) return false;
  handler();
  return true;
}
