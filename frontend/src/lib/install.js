import { useSyncExternalStore } from "react";

// Install banner state. Chromium browsers fire beforeinstallprompt, sometimes
// before React mounts, so it is captured when this module loads. iOS has no
// prompt: the banner shows the Share > Add to Home Screen steps instead.
const DISMISS_KEY = "musebooks.install-banner.dismissed.v1";
const DISMISS_DAYS = 30;

let deferredPrompt = null;
let installed = false;
let dismissed = false;
let snapshot = { kind: "", visible: false };
const listeners = new Set();

export function isStandalone(win = globalThis.window) {
  return Boolean(win?.matchMedia?.("(display-mode: standalone)").matches || win?.navigator?.standalone);
}

export function isIOS(nav = globalThis.navigator) {
  return /iPad|iPhone|iPod/.test(nav?.userAgent || "") || (nav?.platform === "MacIntel" && nav?.maxTouchPoints > 1);
}

export function recentlyDismissed(value, now = Date.now()) {
  const at = Number(value);
  return Number.isFinite(at) && at > 0 && now - at < DISMISS_DAYS * 864e5;
}

// "prompt" (Chromium), "ios" (manual steps), or "" when there is nothing to offer.
export function installKind({ standalone, ios, hasPrompt, installed: done, dismissed: closed }) {
  if (standalone || done || closed) return "";
  if (hasPrompt) return "prompt";
  return ios ? "ios" : "";
}

function update() {
  const kind = typeof window === "undefined" ? "" : installKind({ standalone: isStandalone(), ios: isIOS(), hasPrompt: Boolean(deferredPrompt), installed, dismissed });
  if (kind !== snapshot.kind) snapshot = { kind, visible: Boolean(kind) };
  listeners.forEach(listener => listener());
}

export function startInstallTracking() {
  if (typeof window === "undefined") return;
  try { dismissed = recentlyDismissed(localStorage.getItem(DISMISS_KEY)); } catch { /* Private mode: show again next visit. */ }
  window.addEventListener("beforeinstallprompt", event => {
    // Keep Chrome's own mini-infobar away; the banner offers the same prompt.
    event.preventDefault();
    deferredPrompt = event;
    update();
  });
  window.addEventListener("appinstalled", () => { installed = true; deferredPrompt = null; update(); });
  update();
}

export async function promptInstall() {
  const prompt = deferredPrompt;
  if (!prompt) return false;
  deferredPrompt = null; // A prompt can be shown once.
  await prompt.prompt();
  const choice = await prompt.userChoice.catch(() => null);
  if (choice?.outcome === "accepted") installed = true;
  update();
  return choice?.outcome === "accepted";
}

export function dismissInstall() {
  dismissed = true;
  try { localStorage.setItem(DISMISS_KEY, String(Date.now())); } catch { /* Hidden for this visit only. */ }
  update();
}

const subscribe = listener => { listeners.add(listener); return () => listeners.delete(listener); };
export const useInstallBanner = () => useSyncExternalStore(subscribe, () => snapshot, () => snapshot);
