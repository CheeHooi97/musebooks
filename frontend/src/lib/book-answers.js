import { editionListings, formatPrice, priceLabel } from "./price-policy.js";
import { publicationDate } from "./seo.js";

// Direct, citable answers for answer engines and readers, built only from
// recorded facts. The same text is rendered by React, the prerendered HTML and
// the markdown twin, so every reader sees one account of the record.

const isMagazine = book => book?.publicationType === "magazine_issue";
const kind = book => isMagazine(book) ? "magazine issue" : "photobook";
const people = book => (isMagazine(book) && book.coverModels?.length ? book.coverModels : book.models || []).map(person => person.name).filter(Boolean);
const names = list => list.length <= 2 ? list.join(" and ") : `${list.slice(0, -1).join(", ")}, and ${list.at(-1)}`;
const plural = (count, one, many) => `${count} ${count === 1 ? one : many}`;

export function longDate(value) {
  const text = String(value || "");
  const date = new Date(text.length === 4 ? `${text}-01-01` : text.length === 7 ? `${text}-01` : text);
  if (Number.isNaN(date.getTime())) return "";
  if (text.length === 4) return text;
  const options = { timeZone: "UTC", year: "numeric", month: "long", ...(text.length === 7 ? {} : { day: "numeric" }) };
  return date.toLocaleDateString("en-US", options);
}

function datedEditions(book) {
  return (book.editions || []).map(edition => ({ edition, date: publicationDate(edition) })).filter(item => item.date).sort((a, b) => a.date.localeCompare(b.date));
}

// One self-contained lead paragraph.
export function bookFactSummary(book = {}) {
  const title = book.originalTitle;
  if (!title) return "";
  let sentence = `${title}${book.englishTitle && book.englishTitle !== title ? ` (${book.englishTitle})` : ""} is a ${kind(book)}`;
  const featured = people(book);
  if (featured.length) sentence += ` featuring ${names(featured.slice(0, 4))}`;
  if (book.photographer) sentence += `, photographed by ${book.photographer}`;
  const first = datedEditions(book)[0];
  const publisher = first?.edition.publisher || book.editions?.find(edition => edition.publisher)?.publisher;
  if (publisher) sentence += `, published by ${publisher}`;
  if (first) sentence += ` ${first.date.length === 10 ? "on" : "in"} ${longDate(first.date)}`;
  const sentences = [`${sentence}.`];
  const editions = book.editions || [];
  if (editions.length) {
    const formats = [...new Set(editions.map(edition => edition.format).filter(Boolean))];
    sentences.push(`MuseBooks records ${plural(editions.length, "edition", "editions")}${formats.length ? ` (${formats.join(" and ")})` : ""}.`);
  }
  return sentences.join(" ");
}

function offers(book, status) {
  return (book.editions || []).flatMap(edition => editionListings({ ...edition, listings: edition.listings || [] })
    .filter(listing => listing.status === status && Number.isFinite(listing.priceMinor) && listing.currency)
    .map(listing => ({ edition, listing })));
}

// Prices are only compared within one currency; the most common one leads.
function byLeadingCurrency(items) {
  const counts = new Map();
  for (const { listing } of items) counts.set(listing.currency, (counts.get(listing.currency) || 0) + 1);
  const currency = [...counts].sort((a, b) => b[1] - a[1])[0]?.[0];
  return { currency, items: items.filter(item => item.listing.currency === currency), other: items.length - (counts.get(currency) || 0) };
}

const observed = listing => longDate(String(listing.observedAt || "").slice(0, 10));

function currentPriceAnswer(book) {
  const { items, other } = byLeadingCurrency(offers(book, "active"));
  if (!items.length) return `No active offer is recorded for this ${kind(book)}. Past offers and sales, where recorded, are listed with their sources.`;
  const lowest = items.reduce((low, item) => item.listing.priceMinor < low.listing.priceMinor ? item : low);
  const { edition, listing } = lowest;
  let text = `The lowest recorded active offer is ${formatPrice(listing.priceMinor, listing.currency)} (${priceLabel(edition, listing).toLowerCase()}, ${edition.editionLabel}) on ${listing.source?.name || "the source site"}${observed(listing) ? `, observed ${observed(listing)}` : ""}.`;
  if (items.length > 1) text += ` ${plural(items.length, "active offer is", "active offers are")} recorded in ${listing.currency}.`;
  if (other > 0) text += ` ${plural(other, "more is", "more are")} priced in other currencies.`;
  return `${text} Availability reflects the last observation; check the source before purchasing.`;
}

function soldPriceAnswer(book) {
  const { currency, items, other } = byLeadingCurrency(offers(book, "completed"));
  if (!items.length) return `No confirmed completed sale is recorded for this ${kind(book)}. An ended listing alone is not counted as a sale.`;
  const prices = items.map(item => item.listing.priceMinor).sort((a, b) => a - b);
  const dates = items.map(item => String(item.listing.observedAt || "").slice(0, 10)).filter(Boolean).sort();
  const price = value => formatPrice(value, currency);
  const range = dates.length ? `, observed ${dates.length > 1 && dates[0] !== dates.at(-1) ? `from ${longDate(dates[0])} to ${longDate(dates.at(-1))}` : longDate(dates[0])}` : "";
  let text = items.length === 1
    ? `One confirmed completed sale is recorded: ${price(prices[0])}${range}.`
    : `${items.length} confirmed completed sales are recorded in ${currency}${range}, from ${price(prices[0])} to ${price(prices.at(-1))}${items.length >= 3 ? ` (median ${price(prices[Math.floor((prices.length - 1) / 2)])})` : ""}.`;
  if (other > 0) text += ` ${plural(other, "more sale is", "more sales are")} priced in other currencies.`;
  return `${text} Sold prices are marketplace evidence for that copy and condition, not a valuation.`;
}

export function bookAnswers(book = {}) {
  const title = book.originalTitle;
  if (!title) return [];
  const answers = [];
  const dated = datedEditions(book);
  if (dated.length) {
    const lines = dated.map(({ edition, date }) => `${edition.editionLabel}${edition.publisher ? `, ${edition.publisher}` : ""}: ${longDate(date)}`);
    answers.push({ question: `When was ${title} published?`, answer: dated.length === 1 ? `${title} was published ${dated[0].date.length === 10 ? "on" : "in"} ${longDate(dated[0].date)}${dated[0].edition.publisher ? ` by ${dated[0].edition.publisher}` : ""}.` : `Recorded editions: ${lines.join("; ")}.` });
  } else {
    answers.push({ question: `When was ${title} published?`, answer: "The publication date is not recorded yet." });
  }
  const featured = people(book);
  if (featured.length) answers.push({ question: `Who is featured in ${title}?`, answer: `${names(featured)}.` });
  const isbns = [...new Set((book.editions || []).map(edition => edition.isbn).filter(Boolean))];
  if (isbns.length) answers.push({ question: `What is the ISBN of ${title}?`, answer: isbns.length === 1 ? `ISBN ${isbns[0]}.` : `Recorded ISBNs: ${isbns.join(", ")}.` });
  answers.push({ question: `How much does ${title} cost?`, answer: currentPriceAnswer(book) });
  if ((book.editions || []).some(edition => edition.format !== "digital")) answers.push({ question: `What has ${title} sold for?`, answer: soldPriceAnswer(book) });
  return answers;
}
