import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'
import os from 'node:os'
import { fileURLToPath } from 'node:url'

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..')
const read = file => fs.readFileSync(path.join(root, file))

test('manifest is linked and its icons exist at the declared sizes', () => {
  assert.match(read('index.html').toString(), /<link rel="manifest" href="\/manifest\.webmanifest"\/>/)
  const manifest = JSON.parse(read('public/manifest.webmanifest'))
  assert.equal(manifest.display, 'standalone')
  assert.equal(manifest.start_url, '/')
  for (const icon of manifest.icons) {
    const png = read(path.join('public', icon.src))
    assert.equal(`${png.readUInt32BE(16)}x${png.readUInt32BE(20)}`, icon.sizes, icon.src)
  }
  const sizes = manifest.icons.map(icon => `${icon.sizes} ${icon.purpose}`)
  for (const required of ['192x192 any', '512x512 any', '512x512 maskable']) assert.ok(sizes.includes(required), required)
})

function workerScope({ active = null } = {}) {
  const listeners = {}
  const calls = { skipWaiting: 0, notifications: [], opened: [], navigated: [] }
  const self = {
    location: { origin: 'https://musebooks.my' },
    addEventListener: (type, fn) => { listeners[type] = fn },
    skipWaiting: () => { calls.skipWaiting++ },
    registration: { active, showNotification: (title, options) => { calls.notifications.push({ title, ...options }); return Promise.resolve() } },
    clients: { matchAll: async () => [], openWindow: async url => { calls.opened.push(url) } },
  }
  vm.runInNewContext(read('public/sw.js').toString(), { self, URL, Request: class {}, Response: { error: () => null }, caches: { open: async () => ({ add: async () => {} }) }, fetch: () => Promise.reject(new Error('offline')) })
  return { listeners, calls }
}

function loadWorker() {
  const { listeners } = workerScope()
  return request => {
    let handled = false
    listeners.fetch({ request: { method: 'GET', mode: 'cors', headers: new Map(), ...request }, respondWith: response => { handled = true; Promise.resolve(response).catch(() => {}) } })
    return handled
  }
}

test('service worker handles pages and hashed assets only, never the API', () => {
  const handles = loadWorker()
  assert.equal(handles({ url: 'https://musebooks.my/books/test', mode: 'navigate' }), true)
  assert.equal(handles({ url: 'https://musebooks.my/assets/index-abc123.js' }), true)
  for (const request of [
    { url: 'https://musebooks.my/v1/auth/me' },
    { url: 'https://musebooks.my/v1/books', mode: 'navigate' },
    { url: 'https://musebooks.my/v1/auth/oauth/google', mode: 'navigate' },
    { url: 'https://musebooks.my/books/test', mode: 'navigate', method: 'POST' },
    { url: 'https://img.musecards.my/musebooks/covers/a.jpg' },
    { url: 'https://www.googletagmanager.com/gtag/js' },
    { url: 'https://musebooks.my/assets/a.mp4', headers: new Map([['range', 'bytes=0-']]) },
  ]) assert.equal(handles(request), false, request.url)
})

test('updates wait for the visitor; the first install takes over at once', async () => {
  for (const [active, expected] of [[null, 1], [{}, 0]]) {
    const { listeners, calls } = workerScope({ active })
    let done
    listeners.install({ waitUntil: promise => { done = promise } })
    await done
    assert.equal(calls.skipWaiting, expected)
  }
  const { listeners, calls } = workerScope({ active: {} })
  listeners.message({ data: { type: 'SKIP_WAITING' } })
  listeners.message({ data: { type: 'other' } })
  assert.equal(calls.skipWaiting, 1)
})

test('notifications show the message and only ever open MuseBooks pages', async () => {
  const { listeners, calls } = workerScope()
  const push = async data => { let done; listeners.push({ data: { json: () => data }, waitUntil: promise => { done = promise } }); await done; return calls.notifications.at(-1) }
  const shown = await push({ title: 'New on MuseBooks', body: '2 new publications', url: '/', tag: 'new-publications' })
  assert.deepEqual([shown.title, shown.body, shown.tag, shown.data.url, shown.icon], ['New on MuseBooks', '2 new publications', 'new-publications', '/', '/icon-192.png'])
  assert.equal((await push({ title: 'x', url: 'https://evil.example/phish' })).data.url, '/')
  assert.equal((await push({ title: 'x', url: '/books?q=a' })).data.url, '/books?q=a')
  let done
  listeners.notificationclick({ notification: { close() {}, data: { url: 'javascript:alert(1)' } }, waitUntil: promise => { done = promise } })
  await done
  assert.deepEqual(calls.opened, ['/'])
})

test('every web build stamps a new service worker version', async () => {
  const { stampServiceWorker } = await import('../vite.config.js')
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'musebooks-sw-'))
  try {
    fs.copyFileSync(path.join(root, 'public/sw.js'), path.join(dir, 'sw.js'))
    const build = stampServiceWorker(dir, 'build-123')
    const stamped = fs.readFileSync(path.join(dir, 'sw.js'), 'utf8')
    assert.equal(build, 'build-123')
    assert.ok(stamped.includes('const VERSION = "build-123"') && !stamped.includes('__MUSEBOOKS_BUILD__'))
    assert.throws(() => stampServiceWorker(dir), /placeholder/)
  } finally { fs.rmSync(dir, { recursive: true, force: true }) }
})
