import { bookAnswers, bookFactSummary, fitDescription, profileFactSummary } from "./book-answers.js";
import { GUIDES, GUIDE_UPDATED } from "./guides.js";
// Import damage: text stored as question marks. Such pages stay out of the index until repaired.
export const isCorruptText = value => /\?{2,}/.test(String(value || ""));
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
// Separate works can share a title; the credited person tells them apart in results.
function bookHeadline(book) {
  const title = book.englishTitle || book.originalTitle;
  const person = (book.publicationType === "magazine_issue" && book.coverModels?.[0] || book.models?.[0])?.name;
  return person && !title.includes(person) && !book.originalTitle.includes(person) ? `${title} ${person}` : title;
}
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
    ...Object.fromEntries(Object.entries(GUIDES).map(([route, guide]) => [route, [`${guide.en.title} — MuseBooks`, guide.en.description]])),
    "/404": ["Page not found — MuseBooks", "This catalog page could not be found. Explore the MuseBooks photobook catalog."],
  };
  const url = `${siteURL}${path}`;
  const isMagazineIssue = book?.publicationType === "magazine_issue";
  const publicationLabel = isMagazineIssue ? "magazine issue" : "photobook";
  const [title, description] = book ? [`${bookHeadline(book)} — MuseBooks`, bookFactSummary(book) || `${book.originalTitle}: ${publicationLabel} details, editions, and source-backed prices.`] : pages[path] || ["Publication not found — MuseBooks", DEFAULT_DESCRIPTION];
  const answers = book ? bookAnswers(book) : [];
  // A featured person is what the book is about, not necessarily its author.
  const people = (isMagazineIssue && book.coverModels?.length ? book.coverModels : book?.models || []).map(person => ({ "@type": "Person", name: person.name, url: `${siteURL}/models/${encodeURIComponent(person.id)}` }));
  const structuredData = book ? {
    "@context": "https://schema.org", "@graph": [
      { "@type": isMagazineIssue ? "PublicationIssue" : "Book", "@id": `${url}#publication`, name: book.originalTitle, ...(book.englishTitle ? { alternateName: book.englishTitle } : {}), url, ...(book.summary ? { description: book.summary } : {}), ...(book.coverUrl ? { image: book.coverUrl } : {}), ...(people.length ? { about: people } : {}), ...(book.issueNumber ? { issueNumber: book.issueNumber } : {}), ...(book.issueMonth ? { datePublished: book.issueMonth } : {}), ...(book.editions?.[0]?.seriesName ? { isPartOf: { "@type": isMagazineIssue ? "Periodical" : "BookSeries", name: book.editions[0].seriesName } } : {}), workExample: (book.editions || []).map(edition => ({ "@id": `${url}#edition-${encodeURIComponent(edition.id)}` })) },
      ...(book.editions || []).map(edition => ({ "@type": isMagazineIssue ? "PublicationIssue" : "Book", "@id": `${url}#edition-${encodeURIComponent(edition.id)}`, name: `${book.originalTitle} — ${edition.editionLabel}`, exampleOfWork: { "@id": `${url}#publication` }, ...(edition.isbn ? { isbn: edition.isbn } : {}), ...(edition.publisher ? { publisher: { "@type": "Organization", name: edition.publisher } } : {}), ...(publicationDate(edition) ? { datePublished: publicationDate(edition) } : {}), ...(edition.language ? { inLanguage: edition.language } : {}), ...(edition.pageCount ? { numberOfPages: edition.pageCount } : {}), ...(edition.contentSummary ? { description: edition.contentSummary } : {}), ...(edition.format === "digital" ? { bookFormat: "https://schema.org/EBook" } : {}) })),
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: `${siteURL}/` }, { "@type": "ListItem", position: 2, name: book.originalTitle, item: url }] },
      // As in MuseCards: Google no longer shows FAQ rich results here, but Bing
      // and answer engines read the page's visible Q&A as FAQPage markup.
      ...(answers.length ? [{ "@type": "FAQPage", "@id": `${url}#questions`, mainEntity: answers.map(({ question, answer }) => ({ "@type": "Question", name: question, acceptedAnswer: { "@type": "Answer", text: answer } })) }] : []),
    ],
  } : { "@context": "https://schema.org", "@graph": [
    { "@type": path === "/" ? "WebSite" : GUIDES[path] ? "Article" : "WebPage", "@id": `${url}#page`, ...(GUIDES[path] ? { headline: GUIDES[path].en.title, dateModified: GUIDE_UPDATED, author: { "@id": `${siteURL}/#organization` } } : {}), name: title, url, description, publisher: { "@id": `${siteURL}/#organization` }, ...(path === "/" ? { potentialAction: { "@type": "SearchAction", target: `${siteURL}/books?q={search_term_string}`, "query-input": "required name=search_term_string" } } : {}) },
    { "@type": "Organization", "@id": `${siteURL}/#organization`, name: "MuseBooks", url: `${siteURL}/`, logo: `${siteURL}/apple-touch-icon.png`, ...(path === "/about" ? { email: "musecards67@gmail.com" } : {}) },
  ] };
  if (profile) {
    const isModel = path.startsWith("/models/");
    const onlyMagazines = profile.books?.length && profile.books.every(item => item.publicationType === "magazine_issue");
    const profileTitle = `${profile.name} ${onlyMagazines ? "magazine issues" : "photobooks"} — MuseBooks`;
    const alternateName = [...new Set([profile.originalName, profile.englishName, ...String(profile.aliases || "").split(",")].map(name => name?.trim()).filter(name => name && name !== profile.name))];
    const profileDescription = profileFactSummary(profile, isModel ? "models" : "publishers", profile.books || []);
    return { title: profileTitle, description: fitDescription(profileDescription), url, image: profile.coverUrl, structuredData: { "@context": "https://schema.org", "@graph": [
      { "@type": "CollectionPage", name: profileTitle, url, description: profileDescription, about: { "@type": isModel ? "Person" : "Organization", "@id": `${url}#entity`, name: profile.name, url, ...(alternateName.length ? { alternateName } : {}), ...(!isModel && profile.officialUrl ? { sameAs: profile.officialUrl } : {}) }, ...(profile.books?.length ? { mainEntity: { "@type": "ItemList", itemListElement: profile.books.map((item, index) => ({ "@type": "ListItem", position: index + 1, item: { "@type": item.publicationType === "magazine_issue" ? "PublicationIssue" : "Book", name: item.originalTitle, url: `${siteURL}/books/${encodeURIComponent(item.slug)}` } })) } } : {}) },
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: `${siteURL}/` }, { "@type": "ListItem", position: 2, name: path.startsWith("/models/") ? "Models" : "Publishers", item: `${siteURL}/${path.split("/")[1]}` }, { "@type": "ListItem", position: 3, name: profile.name, item: url }] },
    ] }, noindex: isCorruptText(profile.name) };
  }
  return { title, description: fitDescription(description), url, image: book?.coverUrl, structuredData, noindex: ["/404", "/saved", "/login", "/register", "/verify-email", "/forgot-password", "/reset-password", "/account"].includes(path) || (!book && !pages[path]) || isCorruptText(book?.originalTitle) };
}
