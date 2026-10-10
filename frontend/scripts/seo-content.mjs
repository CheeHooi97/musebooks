import { publicationDate } from '../src/lib/seo.js'
import { ABOUT_SECTIONS } from '../src/lib/about.js'
import { editionListings, formatPrice, priceLabel } from '../src/lib/price-policy.js'

export const escape = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]))
export const json = value => JSON.stringify(value).replace(/</g, '\\u003c')
const safeURL = value => /^https?:\/\//i.test(value || '') ? value : ''
const external = (url, label) => safeURL(url) ? `<a href="${escape(url)}" rel="noreferrer">${escape(label)}</a>` : ''
const bookLink = book => `<a href="/books/${encodeURIComponent(book.slug)}">${escape(book.originalTitle)}</a>`
const facts = pairs => `<dl>${pairs.filter(([, value]) => value).map(([label, value]) => `<dt>${escape(label)}</dt><dd>${escape(value)}</dd>`).join('')}</dl>`
const catalog = books => `<ul>${books.map(book => `<li>${bookLink(book)}${book.englishTitle ? ` — ${escape(book.englishTitle)}` : ''}</li>`).join('')}</ul>`

export function renderContent(route, { book, profile, books = [], profiles = [], listings = [] } = {}) {
  let content;
  if (book) {
    content = `<h1>${escape(book.originalTitle)}</h1>${safeURL(book.coverUrl) ? `<img src="${escape(book.coverUrl)}" alt="${escape(book.originalTitle)} cover" />` : ""}${book.englishTitle ? `<p>${escape(book.englishTitle)}</p>` : ''}${book.summary ? `<p>${escape(book.summary)}</p>` : ''}<p>${(book.models || []).map(person => `<a href="/models/${encodeURIComponent(person.id)}">${escape(person.name)}</a>`).join(' · ')}</p>${facts([['Photographer', book.photographer], ['Origin', book.origin?.name]])}<h2>Available editions</h2>${(book.editions || []).map(edition => `<section id="edition-${encodeURIComponent(edition.id)}"><h3>${escape(edition.editionLabel)}</h3>${facts([['Format', edition.format], ['Publisher', edition.publisher], ['Published', publicationDate(edition)], ['ISBN', edition.isbn], ['Language', edition.language], ['Pages', edition.pageCount], ['Dimensions', edition.dimensions], ['Market', edition.editionMarket]])}${edition.publisherProfile ? `<p><a href="/publishers/${encodeURIComponent(edition.publisherProfile.id)}">${escape(edition.publisherProfile.name)} photobooks</a></p>` : ''}${edition.contentSummary ? `<p>${escape(edition.contentSummary)}</p>` : ''}<p>${external(edition.metadataSourceUrl, 'Edition metadata source')}</p><h4>Source-backed prices</h4><p>Original currencies. Availability reflects the last recorded observation.</p><ul>${editionListings({ ...edition, listings: edition.listings || [] }).map(item => `<li>${escape(item.source.name)}: ${escape(priceLabel(edition, item))}, ${escape(formatPrice(item.priceMinor, item.currency))}. ${escape(item.condition || 'Condition not recorded')}. ${escape(item.shippingText || 'Shipping and taxes not recorded')}. Observed ${escape(item.observedAt || 'date not recorded')}. ${external(item.url, 'View source')}</li>`).join('')}</ul></section>`).join('')}`;
  } else if (profile) {
    content = `<h1>${escape(profile.name)}</h1>${facts([['Original name', profile.originalName], ['English name', profile.englishName]])}<p>${external(profile.officialUrl, 'Profile source')}</p><h2>Photobooks</h2>${catalog(books)}`;
  } else if (route === '/about') {
    content = `<h1>About MuseBooks</h1>${ABOUT_SECTIONS.map(([title, text]) => `<section><h2>${escape(title)}</h2><p>${escape(text)}</p></section>`).join('')}<p><a href="mailto:musecards67@gmail.com">Send a catalog correction</a></p>`;
  } else if (route === '/404') {
    content = '<h1>Page not found</h1><p>This catalog page could not be found.</p><a href="/">Explore photobooks</a>';
  } else if (route === '/privacy-policy') {
    content = '<h1>Privacy Policy</h1><p>MuseBooks stores saved collections and interface preferences in browser storage on your device. They are not synced to a MuseBooks account or uploaded to the catalog API.</p><h2>Website analytics</h2><p>The website uses Google Analytics. Catalog source links open external sites with their own privacy practices.</p><h2>Contact</h2><p>For privacy questions or data requests, email <a href="mailto:musecards67@gmail.com">musecards67@gmail.com</a> and identify MuseBooks in your message.</p>';
  } else if (route === '/models' || route === '/publishers') {
    content = `<h1>${route === '/models' ? 'Models & featured people' : 'Photobook publishers'}</h1><ul>${profiles.map(entry => `<li><a href="${route}/${encodeURIComponent(entry.id)}">${escape(entry.name)}</a></li>`).join('')}</ul>`;
  } else if (route === '/active' || route === '/sold') {
    content = `<h1>${route === '/active' ? 'Active photobook listings' : 'Sold photobook listings'}</h1><p>${route === '/sold' ? 'Confirmed completed physical marketplace sales. Ended offers are separate.' : 'Available at the last recorded observation; check the source before purchasing.'}</p><ul>${listings.map(item => `<li><a href="/books/${encodeURIComponent(item.workSlug)}">${escape(item.workTitle)}</a> — ${escape(item.editionLabel)}, ${escape(item.source?.name)}, ${escape(formatPrice(item.priceMinor, item.currency))}, ${escape(item.condition || 'Condition not recorded')}. Observed ${escape(item.observedAt || 'date not recorded')}. ${external(item.url, 'View source')}</li>`).join('')}</ul>`;
  } else if (route === '/japan') {
    content = '<h1>Japan marketplace listings</h1><p>A snapshot from Yahoo! JAPAN Auctions, Yahoo! Flea Market, and Rakuma. Compare captured bids, fixed asks, and completed prices. Bundle prices apply to the whole listing. Unmatched records are shown separately from verified catalog books.</p><p>Open a source listing to check its current status and details.</p>';
  } else {
    content = `<h1>MuseBooks photobook catalog</h1><p>Discover published photobooks from Japan, Taiwan, China, and Malaysia. Compare physical and digital editions and source-backed prices.</p>${catalog(books)}`;
  }
  return `<div class="site-shell"><header class="site-header"><a href="/">MuseBooks</a><nav aria-label="Main navigation"><a href="/models">Models</a> · <a href="/publishers">Publishers</a> · <a href="/active">Active listings</a> · <a href="/sold">Sold listings</a> · <a href="/japan">Japan marketplace</a> · <a href="/about">About</a></nav></header><main id="main-content" class="seo-static-content">${content}</main><footer><a href="/about">Catalog methodology and corrections</a> · <a href="/privacy-policy">Privacy Policy</a></footer></div>`;
}
