export function normalizeSiteURL(value) {
  const url = new URL(value);
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("Invalid canonical site origin");
  return url.origin;
}
export const SITE_URL = normalizeSiteURL(import.meta.env?.VITE_SITE_URL || (typeof process !== "undefined" ? process.env.VITE_SITE_URL : "") || "https://musebooks.my");
export function hasSearchFilters(search = "") {
  return [...new URLSearchParams(search)].some(([key, value]) => value && ["q", "origin", "format", "publicationType", "language", "year", "source", "model", "publisher", "availability"].includes(key));
}
export function publicationDate(edition) {
  const date = edition.releaseDate?.slice(0, 10);
  if (!date) return "";
  return edition.releasePrecision === "year" ? date.slice(0, 4) : edition.releasePrecision === "month" ? date.slice(0, 7) : date;
}
export const DEFAULT_DESCRIPTION = "Discover model, idol, influencer, and celebrity photobooks and magazine issues. Explore publication dates, cover credits, editions, publishers, and source-backed prices.";
export function pageSeo(path = "/", book, profile, siteURL = SITE_URL) {
  const pages = {
    "/": ["MuseBooks — Photobook and magazine catalog", DEFAULT_DESCRIPTION],
    "/books": ["Browse photobooks and magazine issues — MuseBooks", "Browse every verified photobook and magazine issue by origin, format and availability, with editions and source-backed prices."],
    "/saved": ["Saved collection — MuseBooks", "Publications you saved on this device."],
    "/login": ["Sign in — MuseBooks", "Sign in to MuseBooks with Google or your verified email and password."],
    "/register": ["Create account — MuseBooks", "Create your MuseBooks account with Google or email and password."],
    "/verify-email": ["Verify your email — MuseBooks", "Verify your MuseBooks email address with your emailed code."],
    "/forgot-password": ["Forgot password — MuseBooks", "Request a code to reset your MuseBooks password."],
    "/reset-password": ["Reset password — MuseBooks", "Choose a new password for your MuseBooks account."],
    "/account": ["Your account — MuseBooks", "Manage your MuseBooks sign-in."],
    "/models": ["Models & cover credits — MuseBooks", "Explore photobooks and magazine issues by models, idols, influencers, and entertainers, with cover credits and edition records."],
    "/publishers": ["Publishers — MuseBooks", "Browse photobook publishers and magazine issue sources with source-backed catalog records."],
    "/active": ["Active publication listings — MuseBooks", "Browse available photobook and magazine issue offers. Compare source prices and follow retailer and marketplace links."],
    "/sold": ["Sold publication listings — MuseBooks", "Explore completed physical publication marketplace sales, with original source prices and edition context."],
    "/japan": ["Japan marketplace photobook listings — MuseBooks", "Browse captured photobook listings from Japanese marketplaces, compare current bids, fixed asks, and completed prices, and follow each source listing."],
    "/privacy-policy": ["Privacy Policy — MuseBooks", "Learn how MuseBooks handles saved collections, account preferences, website analytics, and privacy questions."],
    "/about": ["About MuseBooks — Photobook catalog methodology", "How MuseBooks records photobooks, editions, source-backed offers, and completed physical sales. Catalog scope, sources, and corrections."],
    "/404": ["Page not found — MuseBooks", "This catalog page could not be found. Explore the MuseBooks photobook catalog."],
  };
  const url = `${siteURL}${path}`;
  const isMagazineIssue = book?.publicationType === "magazine_issue";
  const publicationLabel = isMagazineIssue ? "magazine issue" : "photobook";
  const [title, description] = book ? [`${book.englishTitle || book.originalTitle} — MuseBooks`, book.summary || `Explore ${book.originalTitle}, its ${publicationLabel} details, editions, and source-backed prices.`] : pages[path] || ["Publication not found — MuseBooks", DEFAULT_DESCRIPTION];
  const structuredData = book ? {
    "@context": "https://schema.org", "@graph": [
      { "@type": isMagazineIssue ? "PublicationIssue" : "Book", "@id": `${url}#publication`, name: book.originalTitle, ...(book.englishTitle ? { alternateName: book.englishTitle } : {}), url, ...(book.summary ? { description: book.summary } : {}), ...(book.coverUrl ? { image: book.coverUrl } : {}), ...(book.issueNumber ? { issueNumber: book.issueNumber } : {}), ...(book.issueMonth ? { datePublished: book.issueMonth } : {}), ...(book.editions?.[0]?.seriesName ? { isPartOf: { "@type": isMagazineIssue ? "Periodical" : "BookSeries", name: book.editions[0].seriesName } } : {}), workExample: (book.editions || []).map(edition => ({ "@id": `${url}#edition-${encodeURIComponent(edition.id)}` })) },
      ...(book.editions || []).map(edition => ({ "@type": isMagazineIssue ? "PublicationIssue" : "Book", "@id": `${url}#edition-${encodeURIComponent(edition.id)}`, name: `${book.originalTitle} — ${edition.editionLabel}`, exampleOfWork: { "@id": `${url}#publication` }, ...(edition.isbn ? { isbn: edition.isbn } : {}), ...(edition.publisher ? { publisher: { "@type": "Organization", name: edition.publisher } } : {}), ...(publicationDate(edition) ? { datePublished: publicationDate(edition) } : {}), ...(edition.language ? { inLanguage: edition.language } : {}), ...(edition.pageCount ? { numberOfPages: edition.pageCount } : {}), ...(edition.contentSummary ? { description: edition.contentSummary } : {}), ...(edition.format === "digital" ? { bookFormat: "https://schema.org/EBook" } : {}) })),
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: `${siteURL}/` }, { "@type": "ListItem", position: 2, name: book.originalTitle, item: url }] },
    ],
  } : { "@context": "https://schema.org", "@graph": [
    { "@type": path === "/" ? "WebSite" : "WebPage", "@id": `${url}#page`, name: title, url, description, publisher: { "@id": `${siteURL}/#organization` } },
    { "@type": "Organization", "@id": `${siteURL}/#organization`, name: "MuseBooks", url: `${siteURL}/`, ...(path === "/about" ? { email: "musecards67@gmail.com" } : {}) },
  ] };
  if (profile) {
    const profileTitle = `${profile.name} publications — MuseBooks`;
    const profileDescription = `Explore ${profile.name} photobooks and magazine cover issues, with edition dates and prices from different platforms.`;
    return { title: profileTitle, description: profileDescription.slice(0, 160), url, image: profile.coverUrl, structuredData: { "@context": "https://schema.org", "@graph": [
      { "@type": "CollectionPage", name: profileTitle, url, description: profileDescription, ...(profile.books?.length ? { mainEntity: { "@type": "ItemList", itemListElement: profile.books.map((item, index) => ({ "@type": "ListItem", position: index + 1, item: { "@type": item.publicationType === "magazine_issue" ? "PublicationIssue" : "Book", name: item.originalTitle, url: `${siteURL}/books/${encodeURIComponent(item.slug)}` } })) } } : {}) },
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: `${siteURL}/` }, { "@type": "ListItem", position: 2, name: path.startsWith("/models/") ? "Models" : "Publishers", item: `${siteURL}/${path.split("/")[1]}` }, { "@type": "ListItem", position: 3, name: profile.name, item: url }] },
    ] }, noindex: false };
  }
  return { title, description: description.replace(/\s+/g, " ").trim().slice(0, 160), url, image: book?.coverUrl, structuredData, noindex: ["/404", "/saved", "/login", "/register", "/verify-email", "/forgot-password", "/reset-password", "/account"].includes(path) || (!book && !pages[path]) };
}
