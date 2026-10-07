export const SITE_URL = (import.meta.env?.VITE_SITE_URL || "https://musebooks.my").replace(/\/$/, "");
export const DEFAULT_DESCRIPTION = "Discover model, idol, influencer, and celebrity photobooks. Explore physical and digital editions, publishers, and source-backed active and sold prices.";
export function pageSeo(path = "/", book) {
  const pages = {
    "/": ["MuseBooks — Photobook archive", DEFAULT_DESCRIPTION],
    "/models": ["Models & featured people — MuseBooks", "Explore photobooks by models, idols, influencers, and entertainers, with physical and digital edition records."],
    "/publishers": ["Photobook publishers — MuseBooks", "Browse photobook publishers and discover their physical and digital editions with source-backed catalog records."],
    "/active": ["Active photobook listings — MuseBooks", "Browse available physical and digital photobook offers. Compare source prices and follow retailer and marketplace links."],
    "/sold": ["Sold photobook listings — MuseBooks", "Explore completed physical photobook marketplace sales, with original source prices and edition context."],
    "/privacy-policy": ["Privacy Policy — MuseBooks", "Learn how MuseBooks handles saved collections, account preferences, website analytics, and privacy questions."],
  };
  const url = `${SITE_URL}${path}`;
  const [title, description] = book ? [`${book.englishTitle || book.originalTitle} — MuseBooks`, book.summary || `Explore ${book.originalTitle}, its physical and digital editions, publication details, and source-backed prices.`] : pages[path] || ["Photobook not found — MuseBooks", DEFAULT_DESCRIPTION];
  const structuredData = book ? {
    "@context": "https://schema.org", "@graph": [
      { "@type": "Book", "@id": `${url}#book`, name: book.originalTitle, ...(book.englishTitle ? { alternateName: book.englishTitle } : {}), url, ...(book.summary ? { description: book.summary } : {}), ...(book.coverUrl ? { image: book.coverUrl } : {}) },
      { "@type": "BreadcrumbList", itemListElement: [{ "@type": "ListItem", position: 1, name: "Home", item: `${SITE_URL}/` }, { "@type": "ListItem", position: 2, name: book.originalTitle, item: url }] },
    ],
  } : { "@context": "https://schema.org", "@type": path === "/" ? "WebSite" : "WebPage", name: title, url, description };
  return { title, description: description.replace(/\s+/g, " ").trim().slice(0, 160), url, image: book?.coverUrl, structuredData, noindex: !book && !pages[path] };
}
