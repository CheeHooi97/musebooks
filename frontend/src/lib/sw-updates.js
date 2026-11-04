import { useSyncExternalStore } from "react";

// Service worker registration and "new version" prompts. Each release ships a
// new sw.js (see stampServiceWorker in vite.config.js); it installs in the
// background and waits until the visitor chooses Update.
const CHECK_EVERY = 30 * 60 * 1000;

let registration = null;
let waiting = null;
let snoozed = null;
let reloading = false;
let registering = false;
const ready = [];
const listeners = new Set();
let snapshot = { available: false };

function emit() {
  const available = Boolean(waiting) && waiting !== snoozed;
  if (available !== snapshot.available) snapshot = { available };
  listeners.forEach(listener => listener());
}

// A worker waiting behind a page that is already controlled is an update; on
// the very first visit there is nothing to update.
function track(worker) {
  if (!worker || !navigator.serviceWorker.controller) return;
  waiting = worker;
  emit();
}

function watch(reg) {
  track(reg.waiting);
  reg.addEventListener("updatefound", () => {
    const next = reg.installing;
    next?.addEventListener("statechange", () => { if (next.state === "installed") track(next); });
  });
}

export function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) return;
  registering = true;
  const register = () => navigator.serviceWorker.register("/sw.js").then(reg => {
    registration = reg;
    watch(reg);
    ready.splice(0).forEach(resolve => resolve(reg));
    const check = () => reg.update().catch(() => undefined);
    setInterval(check, CHECK_EVERY);
    document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") check(); });
  }).catch(() => { registering = false; ready.splice(0).forEach(resolve => resolve(null)); });
  if (document.readyState === "complete") register();
  else window.addEventListener("load", register, { once: true });
}

// Resolves once the worker is registered (for push subscriptions), or with
// null where none is (development, unsupported browsers).
export function serviceWorkerRegistration() {
  if (registration) return Promise.resolve(registration);
  if (!registering) return Promise.resolve(null);
  return new Promise(resolve => ready.push(resolve));
}

export function applyUpdate() {
  if (!waiting) return;
  // Reload only for an update the visitor accepted, not for the first install.
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (reloading) return;
    reloading = true;
    window.location.reload();
  }, { once: true });
  waiting.postMessage({ type: "SKIP_WAITING" });
}

// "Later" hides this version's prompt until the next release or visit.
export function snoozeUpdate() {
  snoozed = waiting;
  emit();
}

const subscribe = listener => { listeners.add(listener); return () => listeners.delete(listener); };
export const useUpdateAvailable = () => useSyncExternalStore(subscribe, () => snapshot, () => snapshot).available;
