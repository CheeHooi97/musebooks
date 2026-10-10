export function normalizeSiteURL(value) {
  const url = new URL(value);
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("Invalid canonical site origin");
  return url.origin;
}
export const SITE_URL = normalizeSiteURL(import.meta.env?.VITE_SITE_URL || (typeof process !== "undefined" ? process.env.VITE_SITE_URL : "") || "https://musebooks.my");
export function hasSearchFilters(search = "") {
  return [...new URLSearchParams(search)].some(([key, value]) => value && ["q", "origin", "format", "language", "year", "source", "model", "publisher", "availability"].includes(key));
}
export function publicationDate(edition) {
  const date = edition.releaseDate?.slice(0, 10);
  if (!date) return "";
  return edition.releasePrecision === "year" ? date.slice(0, 4) : edition.releasePrecision === "month" ? date.slice(0, 7) : date;
}
export const DEFAULT_DESCRIPTION = "Discover model, idol, influencer, and celebrity photobooks. Explore physical and digital editions, publishers, and source-backed active and sold prices.";
export function pageSeo(path = "/", book, profile, siteURL = SITE_URL) {
  const pages = {
    "/": ["MuseBooks — Photobook archive", DEFAULT_DESCRIPTION],
    "/models": ["Models & featured people — MuseBooks", "Explore photobooks by models, idols, influencers, and entertainers, with physical and digital edition records."],
    "/publishers": ["Photobook publishers — MuseBooks", "Browse photobook publishers and discover their physical and digital editions with source-backed catalog records."],
    "/active": ["Active photobook listings — MuseBooks", "Browse available physical and digital photobook offers. Compare source prices and follow retailer and marketplace links."],
    "/sold": ["Sold photobook listings — MuseBooks", "Explore completed physical photobook marketplace sales, with original source prices and edition context."],
    "/japan": ["Japan marketplace photobook listings — MuseBooks", "Browse captured photobook listings from Japanese marketplaces, compare current bids, fixed asks, and completed prices, and follow each source listing."],
    "/privacy-policy": ["Privacy Policy — MuseBooks", "Learn how MuseBooks handles saved collections, account preferences, website analytics, and privacy questions."],
    "/about": ["About MuseBooks — Photobook catalog methodology", "How MuseBooks records photobooks, editions, source-backed offers, and completed physical sales. Catalog scope, sources, and corrections."],
    "/404": ["Page not found — MuseBooks", "This catalog page could not be found. Explore the MuseBooks photobook catalog."],
  };
  const url = `${siteURL}${path}`;
  const [title, description] = book ? [`${book.englishTitle || book.originalTitle} — MuseBooks`, book.summary || `Explore ${book.originalTitle}, its physical and digital editions, publication details, and source-backed prices.`] : pages[path] || ["Photobook not found — MuseBooks", DEFAULT_DESCRIPTION];
  const structuredData = book ? {
    "@context": "https://schema.org", "@graph": [
      { "@type": "Book", "@id": `${url}#book`, name: book.originalTitle, ...(book.englishTitle ? { alternateName: book.englishTitle } : {}), url, ...(book.summary ? { description: book.summary } : {}), ...(book.coverUrl ? { image: book.coverUrl } : {}), workExample: (book.editions || []).map(edition => ({ "@id": `${url}#edition-${encodeURIComponent(edition.id)}` })) },
      ...(book.editions || []).map(edition => ({ "@type": "Book", "@id": `${url}#edition-${encodeURIComponent(edition.id)}`, name: `${book.originalTitle} — ${edition.editionLabel}`, exampleOfWork: { "@id": `${url}#book` }, ...(edition.isbn ? { isbn: edition.isbn } : {}), ...(edition.publisher ? { publisher: { "@type": "Organization", name: edition.publisher } } : {}), ...(publicationDate(edition) ? { datePublished: publicationDate(edition) } : {}), ...(edition.language ? { inLanguage: edition.language } : {}), ...(edition.pageCount ? { numberOfPages: edition.pageCount } : {}), ...(edition.contentSummary ? { description: edition.contentSummary } : {}), ...(edition.format === "digital" ? { bookFormat: "https://schema.org/EBook" } : {}) })),
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: `${siteURL}/` }, { "@type": "ListItem", position: 2, name: book.originalTitle, item: url }] },
    ],
  } : { "@context": "https://schema.org", "@graph": [
    { "@type": path === "/" ? "WebSite" : "WebPage", "@id": `${url}#page`, name: title, url, description, publisher: { "@id": `${siteURL}/#organization` } },
    { "@type": "Organization", "@id": `${siteURL}/#organization`, name: "MuseBooks", url: `${siteURL}/`, ...(path === "/about" ? { email: "musecards67@gmail.com" } : {}) },
  ] };
  if (profile) {
    const profileTitle = `${profile.name} photobooks — MuseBooks`;
    const profileDescription = `Explore ${profile.name} photobooks, physical and digital editions, and prices from different platforms.`;
    return { title: profileTitle, description: profileDescription.slice(0, 160), url, image: profile.coverUrl, structuredData: { "@context": "https://schema.org", "@graph": [
      { "@type": "CollectionPage", name: profileTitle, url, description: profileDescription, ...(profile.books?.length ? { mainEntity: { "@type": "ItemList", itemListElement: profile.books.map((item, index) => ({ "@type": "ListItem", position: index + 1, item: { "@type": "Book", name: item.originalTitle, url: `${siteURL}/books/${encodeURIComponent(item.slug)}` } })) } } : {}) },
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: `${siteURL}/` }, { "@type": "ListItem", position: 2, name: path.startsWith("/models/") ? "Models" : "Publishers", item: `${siteURL}/${path.split("/")[1]}` }, { "@type": "ListItem", position: 3, name: profile.name, item: url }] },
    ] }, noindex: false };
  }
  return { title, description: description.replace(/\s+/g, " ").trim().slice(0, 160), url, image: book?.coverUrl, structuredData, noindex: path === "/404" || (!book && !pages[path]) };
}
