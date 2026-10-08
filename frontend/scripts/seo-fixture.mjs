// Synthetic records for build and browser verification only.
export const profile = { id: 'test-person', name: 'Test Person', workCount: 1, editionCount: 1 };
export const publisher = { id: 'test-publisher', name: 'Test Publisher', workCount: 1, editionCount: 1 };
export const listing = { id: 'offer', workSlug: 'test-book', workTitle: 'Test Photobook', editionLabel: 'First edition', source: { id: 'shop', name: 'Test Shop', kind: 'marketplace', region: 'JP', photobookFormat: 'physical' }, format: 'physical', status: 'active', priceCategory: 'marketplace_active', priceMinor: 2500, currency: 'JPY', condition: 'Used', url: 'https://example.com/offer', observedAt: '2026-10-01T00:00:00Z' };
export const book = { id: 'test-work', slug: 'test-book', originalTitle: 'Test Photobook', englishTitle: 'Test Photobook', summary: 'A sourced test publication.', origin: { code: 'JP', name: 'Japan' }, models: [profile], featuredNames: ['Test Person'], editions: [{ id: 'test-edition', editionLabel: 'First edition', format: 'physical', publisher: publisher.name, publisherProfile: publisher, isbn: '9780000000002', language: 'ja', releaseDate: '2025-01-01T00:00:00Z', releasePrecision: 'year', pageCount: 96, dimensions: 'A4', contentSummary: 'Verified edition description.', metadataSourceUrl: 'https://example.com/metadata', listings: [listing] }] };
export function fixtureResponse(url) {
  const { pathname, searchParams } = new URL(url);
  const page = Number(searchParams.get('page') || 1);
  const list = items => ({ items, total: items.length, totalPages: items.length ? 1 : 0, page, pageSize: 50 });
  if (pathname === '/v1/books') return list([book]);
  if (pathname === '/v1/books/test-book') return book;
  if (pathname === '/v1/models') return list([profile]);
  if (pathname === '/v1/publishers') return list([publisher]);
  if (pathname === '/v1/models/test-person') return profile;
  if (pathname === '/v1/publishers/test-publisher') return publisher;
  if (/^\/v1\/(models|publishers)\/[^/]+\/books$/.test(pathname)) return list([book]);
  if (pathname === '/v1/listings') return list(searchParams.get('status') === 'sold' ? [] : [listing]);
  if (pathname === '/v1/origins') return [{ ...book.origin, count: 1 }];
  if (pathname === '/v1/sources') return [listing.source];
  return null;
}
