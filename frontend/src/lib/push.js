import { apiUrl } from "./api.js";
import { isIOS, isStandalone } from "./install.js";
import { isMobileApp } from "./platform.js";
import { serviceWorkerRegistration } from "./sw-updates.js";

// New-publication notifications (standard Web Push; no Firebase). Like
// MuseCards alerts they belong to a signed-in account.

// "supported", "ios-install" (iPhone/iPad must add the site to the Home Screen
// first), "denied" (blocked in site settings) or "unsupported".
export function pushSupport(win = globalThis.window) {
  if (!win || isMobileApp) return "unsupported";
  const capable = "serviceWorker" in win.navigator && "PushManager" in win && "Notification" in win;
  if (!capable) return isIOS(win.navigator) && !isStandalone(win) ? "ios-install" : "unsupported";
  return win.Notification.permission === "denied" ? "denied" : "supported";
}

async function pushRequest(path, data) {
  const response = await fetch(apiUrl(`/v1/push/${path}`), {
    method: data === undefined ? "GET" : "POST",
    headers: { Accept: "application/json", ...(data === undefined ? {} : { "Content-Type": "application/json" }) },
    credentials: "include",
    ...(data === undefined ? {} : { body: JSON.stringify(data) }),
    signal: AbortSignal.timeout(20000),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.error) {
    const error = new Error(payload.errmsg || "We could not connect. Please try again.");
    error.status = response.status;
    error.code = payload.code;
    throw error;
  }
  return payload.result;
}

export function serverKey(base64url) {
  const text = atob(base64url.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(base64url.length / 4) * 4, "="));
  return Uint8Array.from(text, char => char.charCodeAt(0));
}

const sameKey = (subscription, publicKey) => {
  const current = subscription.options?.applicationServerKey;
  if (!current) return true;
  const expected = serverKey(publicKey);
  const actual = new Uint8Array(current);
  return actual.length === expected.length && actual.every((byte, index) => byte === expected[index]);
};

async function browserSubscription() {
  const registration = await serviceWorkerRegistration();
  return registration ? { registration, subscription: await registration.pushManager.getSubscription() } : { registration: null, subscription: null };
}

// Whether this device is on for the signed-in account.
export async function pushEnabled() {
  const { subscription } = await browserSubscription();
  if (!subscription) return false;
  const result = await pushRequest(`subscription?${new URLSearchParams({ endpoint: subscription.endpoint })}`);
  return Boolean(result?.subscribed);
}

export async function enablePush(language, confirmation) {
  // Call the browser permission API before any network or service worker waits,
  // while the user's button tap still counts as a gesture.
  if (await Notification.requestPermission() !== "granted") {
    const error = new Error("Notifications are blocked for this site. Allow them in your browser's site settings, then try again.");
    error.code = "denied";
    throw error;
  }
  const config = await pushRequest("config");
  if (!config?.enabled) throw new Error("Notifications are not available yet. Please try again later.");
  const { registration, subscription: existing } = await browserSubscription();
  if (!registration) throw new Error("Notifications are not available in this browser.");
  let subscription = existing;
  // A subscription made with another server key cannot be reused.
  if (subscription && !sameKey(subscription, config.publicKey)) {
    await subscription.unsubscribe();
    subscription = null;
  }
  subscription ||= await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: serverKey(config.publicKey) });
  await pushRequest("subscription", { ...subscription.toJSON(), language });
  if (confirmation) registration.showNotification(confirmation.title, { body: confirmation.body, icon: "/icon-192.png", badge: "/icon-192.png", tag: "musebooks-push-on" }).catch(() => undefined);
}

// Turns this device off: on the server for the account, then in the browser.
export async function disablePush() {
  const { subscription } = await browserSubscription();
  if (!subscription) return;
  try { await pushRequest("subscription/remove", { endpoint: subscription.endpoint }); }
  finally { await subscription.unsubscribe().catch(() => undefined); }
}
