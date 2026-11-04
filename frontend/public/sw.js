// MuseBooks service worker. Pages are static public releases (never per-user),
// so visited pages may be kept for offline reading. The API (/v1/: catalog,
// sign-in, accounts) is never cached or intercepted.
// The build replaces the stamp below, so every release is a new worker and
// browsers offer the update (see src/lib/sw-updates.js).
const VERSION = "__MUSEBOOKS_BUILD__";
const PAGES = `musebooks-pages-${VERSION}`;
const ASSETS = `musebooks-assets-${VERSION}`;
const OFFLINE = "/offline.html";
const PAGE_LIMIT = 60;

self.addEventListener("install", event => {
  // The first install takes over at once. An update waits until the visitor
  // chooses Update, so a page never switches files under them.
  const firstInstall = !self.registration.active;
  event.waitUntil(caches.open(PAGES).then(cache => cache.add(new Request(OFFLINE, { cache: "reload" }))).then(() => firstInstall && self.skipWaiting()));
});

self.addEventListener("message", event => {
  if (event.data?.type === "SKIP_WAITING") self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(key => key.startsWith("musebooks-") && key !== PAGES && key !== ASSETS).map(key => caches.delete(key))))
    .then(() => self.clients.claim()));
});

// Which requests the worker handles; everything else goes straight to the network.
function strategy(request) {
  if (request.method !== "GET" || request.headers.has("range")) return "";
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.startsWith("/v1/") || url.pathname === "/v1") return "";
  if (request.mode === "navigate") return "page";
  // Built files carry a content hash in their name, so a cached copy never goes stale.
  if (url.pathname.startsWith("/assets/")) return "asset";
  return "";
}

async function trimPages(cache) {
  // Keys come back oldest first; keep the newest PAGE_LIMIT pages and the offline page.
  const pages = (await cache.keys()).filter(key => new URL(key.url).pathname !== OFFLINE);
  await Promise.all(pages.slice(0, Math.max(0, pages.length - PAGE_LIMIT)).map(key => cache.delete(key)));
}

async function page(request) {
  const cache = await caches.open(PAGES);
  try {
    const response = await fetch(request);
    if (response.ok && response.type === "basic") {
      await cache.put(request, response.clone());
      trimPages(cache);
    }
    return response;
  } catch {
    return (await cache.match(request, { ignoreSearch: true })) || (await cache.match(OFFLINE)) || Response.error();
  }
}

async function asset(request) {
  const cache = await caches.open(ASSETS);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok && response.type === "basic") await cache.put(request, response.clone());
  return response;
}

self.addEventListener("fetch", event => {
  const kind = strategy(event.request);
  if (kind === "page") event.respondWith(page(event.request));
  else if (kind === "asset") event.respondWith(asset(event.request));
});

// Notifications only ever open a MuseBooks page.
function sitePath(value) {
  try {
    const url = new URL(value || "/", self.location.origin);
    return url.origin === self.location.origin ? url.pathname + url.search : "/";
  } catch { return "/"; }
}

self.addEventListener("push", event => {
  let message = {};
  try { message = event.data?.json() || {}; } catch { message = { body: event.data?.text() }; }
  event.waitUntil(self.registration.showNotification(String(message.title || "MuseBooks").slice(0, 120), {
    body: String(message.body || "").slice(0, 300),
    icon: "/icon-192.png",
    badge: "/icon-192.png",
    tag: String(message.tag || "musebooks"),
    data: { url: sitePath(message.url) },
  }));
});

self.addEventListener("notificationclick", event => {
  event.notification.close();
  const path = sitePath(event.notification.data?.url);
  event.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(windows => {
    const open = windows.find(client => new URL(client.url).origin === self.location.origin);
    if (open) return open.focus().then(client => client.navigate ? client.navigate(path) : client);
    return self.clients.openWindow(path);
  }));
});
