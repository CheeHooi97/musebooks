import assert from 'node:assert/strict'
import test from 'node:test'
import worker, { ROBOTS_TXT, listingImageSourceURL, objectKeyFromPath, verifySignature } from './index.js'

// Shared with backend/storage/media_test.go so both sides agree on the
// signed message and encoding.
const SECRET = 'test-media-signing-secret-0123456789abcdef'
const KEY = 'musebooks/sample cover.jpg'
const EXP = 1800000000
const SIGNATURE = 'z87t2-ZSbCgeeJ2JsNFsygvc_9PEXBineRN6ZkjD3jA'

test('accepts the signature the Go API produces', async () => {
  assert.equal(await verifySignature(SECRET, KEY, EXP, SIGNATURE), true)
})

test('rejects a signature for another key, expiry or secret', async () => {
  assert.equal(await verifySignature(SECRET, 'musebooks/other.jpg', EXP, SIGNATURE), false)
  assert.equal(await verifySignature(SECRET, KEY, EXP + 1, SIGNATURE), false)
  assert.equal(await verifySignature('another-secret', KEY, EXP, SIGNATURE), false)
  assert.equal(await verifySignature(SECRET, KEY, EXP, ''), false)
  assert.equal(await verifySignature('', KEY, EXP, SIGNATURE), false)
})

test('decodes object keys from escaped paths', () => {
  assert.equal(objectKeyFromPath('/musebooks/sample%20cover.jpg'), KEY)
  assert.equal(objectKeyFromPath('/musebooks/covers/a.jpg'), 'musebooks/covers/a.jpg')
})

test('rejects traversal and empty paths', () => {
  assert.equal(objectKeyFromPath('/'), '')
  assert.equal(objectKeyFromPath('/musebooks/%2E%2E/secret.jpg'), '')
  assert.equal(objectKeyFromPath('/musebooks/a%2Fb.jpg'), '')
  assert.equal(objectKeyFromPath('/musebooks/a%5Cb.jpg'), '')
  assert.equal(objectKeyFromPath('/musebooks/%E0%A4%A.jpg'), '')
})

test('decodes only signed-path marketplace image URLs from the exact host allowlist', () => {
  const keyFor = (source) => `musebooks/listing-thumbnails/v1/${Buffer.from(source).toString('base64url')}`
  const source = 'https://auctions.c.yimg.jp/images/sample.jpg?size=1200'
  assert.equal(listingImageSourceURL(keyFor(source)), source)
  assert.equal(listingImageSourceURL(keyFor('https://evil.example/image.jpg')), '')
  assert.equal(listingImageSourceURL(keyFor('http://auctions.c.yimg.jp/images/sample.jpg')), '')
  assert.equal(listingImageSourceURL(keyFor('https://auctions.c.yimg.jp/images/sample.svg')), '')
  assert.equal(listingImageSourceURL('musebooks/listing-thumbnails/v1/%2Fetc%2Fpasswd'), '')
})

test('serves nothing outside KEY_PREFIX', async () => {
  const env = { KEY_PREFIX: 'musebooks/', MEDIA_SIGNING_SECRET: SECRET, MEDIA_BUCKET: { get: () => assert.fail('bucket read') } }
  const response = await worker.fetch(new Request('https://media.example.test/images/card.jpg?exp=1&sig=x'), env, {})
  assert.equal(response.status, 404)
})

test('answers robots.txt without a signature', async () => {
  const response = await worker.fetch(new Request('https://media.musebooks.my/robots.txt'), {}, {})
  assert.equal(response.status, 200)
  assert.equal(await response.text(), ROBOTS_TXT)
})
