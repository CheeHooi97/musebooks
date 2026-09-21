"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CatalogBook,
  Edition,
  Format,
  Origin,
  seedBooks,
  seedOrigins,
} from "../lib/catalog";

type IconName =
  | "search"
  | "bookmark"
  | "user"
  | "chevron"
  | "external"
  | "share"
  | "book"
  | "close";

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };
  if (name === "search") {
    return <svg {...common}><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" /></svg>;
  }
  if (name === "bookmark") {
    return <svg {...common}><path d="M6.5 4.5A1.5 1.5 0 0 1 8 3h8a1.5 1.5 0 0 1 1.5 1.5V21l-5.5-3.2L6.5 21V4.5Z" /></svg>;
  }
  if (name === "user") {
    return <svg {...common}><circle cx="12" cy="8" r="3.2" /><path d="M5.5 20c.7-3.2 2.9-5 6.5-5s5.8 1.8 6.5 5" /></svg>;
  }
  if (name === "chevron") {
    return <svg {...common}><path d="m7 9 5 5 5-5" /></svg>;
  }
  if (name === "external") {
    return <svg {...common}><path d="M14 5h5v5" /><path d="m19 5-8 8" /><path d="M19 13v4.5A1.5 1.5 0 0 1 17.5 19h-13A1.5 1.5 0 0 1 3 17.5v-13A1.5 1.5 0 0 1 4.5 3H9" /></svg>;
  }
  if (name === "share") {
    return <svg {...common}><circle cx="18" cy="5" r="2.2" /><circle cx="6" cy="12" r="2.2" /><circle cx="18" cy="19" r="2.2" /><path d="m8 11 7.8-4.7M8 13l7.8 4.7" /></svg>;
  }
  if (name === "book") {
    return <svg {...common}><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H19v17H7.5A2.5 2.5 0 0 0 5 21.5v-17Z" /><path d="M5 4.5v17M8 6h7" /></svg>;
  }
  return <svg {...common}><path d="m6 6 12 12M18 6 6 18" /></svg>;
}

function formatPrice(priceMinor?: number, currency?: string) {
  if (priceMinor === undefined || !currency) return "Price on site";
  const symbols: Record<string, string> = { JPY: "¥", TWD: "NT$", CNY: "¥", MYR: "RM", USD: "$" };
  return (symbols[currency] || currency) + " " + priceMinor.toLocaleString("en-US");
}

function firstListing(book: CatalogBook) {
  return book.editions.flatMap((item) => item.listings)[0];
}

function editionFormatLabel(format: Format) {
  return format === "digital" ? "Digital edition" : "Physical book";
}

function BookCover({
  book,
  edition: selectedEdition,
  compact = false,
}: {
  book: CatalogBook;
  edition?: Edition;
  compact?: boolean;
}) {
  const image = selectedEdition?.coverUrl || book.coverUrl;
  return (
    <div className={"cover-art" + (compact ? " cover-art--compact" : "")}>
      {image ? <img src={image} alt="" /> : null}
      <div className="cover-art__wash" />
      <span className="cover-art__mark">{book.originalTitle.slice(0, 2)}</span>
      <span className="cover-art__title">{book.englishTitle || book.originalTitle}</span>
    </div>
  );
}

function FilterGroup({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="filter-group">
      <div className="filter-group__title">
        <h3>{title}</h3>
        <Icon name="chevron" size={15} />
      </div>
      {children}
    </section>
  );
}

export default function Home() {
  const [books, setBooks] = useState<CatalogBook[]>(seedBooks);
  const [origins, setOrigins] = useState<Origin[]>(seedOrigins);
  const [query, setQuery] = useState("");
  const [origin, setOrigin] = useState("");
  const [format, setFormat] = useState<Format | "">("");
  const [language, setLanguage] = useState("");
  const [availability, setAvailability] = useState("");
  const [selectedId, setSelectedId] = useState("work-tw-hai-bian-de-ri-chang");
  const [selectedEditionId, setSelectedEditionId] = useState("edition-sea-standard");
  const [saved, setSaved] = useState<string[]>([]);
  const [shareState, setShareState] = useState<"idle" | "copied">("idle");
  const [mobileFilters, setMobileFilters] = useState(false);
  const [apiState, setApiState] = useState<"seed" | "live">("seed");

  useEffect(() => {
    try {
      const stored = window.localStorage.getItem("musebooks.collection.v1");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) setSaved(parsed.filter((item): item is string => typeof item === "string"));
      }
    } catch {
      // Collection persistence is best effort for the preview experience.
    }
  }, []);

  useEffect(() => {
    try {
      window.localStorage.setItem("musebooks.collection.v1", JSON.stringify(saved));
    } catch {
      // Collection persistence is best effort for the preview experience.
    }
  }, [saved]);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetch("/v1/books?pageSize=50").then((response) => response.ok ? response.json() : Promise.reject(response.status)),
      fetch("/v1/origins").then((response) => response.ok ? response.json() : Promise.reject(response.status)),
    ])
      .then(([bookResponse, originResponse]) => {
        if (cancelled || !bookResponse.items?.length) return;
        setBooks(bookResponse.items);
        if (originResponse?.length) setOrigins(originResponse);
        setApiState("live");
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredBooks = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    return books.filter((book) => {
      const haystack = [
        book.originalTitle,
        book.englishTitle,
        ...(book.featuredNames || []),
        book.photographer,
      ].filter(Boolean).join(" ").toLocaleLowerCase();
      const matchesQuery = !normalized || haystack.includes(normalized);
      const matchesOrigin = !origin || book.origin.code === origin;
      const matchesFormat = !format || book.editions.some((item) => item.format === format);
      const matchesLanguage = !language || book.editions.some((item) => item.language?.includes(language));
      const matchesAvailability = !availability || book.editions.some((item) => item.listings.some((item) => item.status === availability));
      return matchesQuery && matchesOrigin && matchesFormat && matchesLanguage && matchesAvailability;
    });
  }, [availability, books, format, language, origin, query]);

  const selectedBook = books.find((book) => book.id === selectedId) || filteredBooks[0] || books[0];
  const selectedEdition = selectedBook?.editions.find((item) => item.id === selectedEditionId) || selectedBook?.editions[0];
  const selectedListing = selectedEdition ? selectedEdition.listings[0] : undefined;

  const toggleSaved = (bookId: string) => {
    if (!bookId) return;
    setSaved((current) => current.includes(bookId) ? current.filter((id) => id !== bookId) : [...current, bookId]);
  };

  const shareSelected = async () => {
    if (!selectedBook) return;
    const shareURL = window.location.origin + "#" + selectedBook.slug;
    try {
      await navigator.clipboard?.writeText(shareURL);
    } catch {
      // Clipboard access can be unavailable in local or embedded browsers.
    }
    setShareState("copied");
    window.setTimeout(() => setShareState("idle"), 1800);
  };

  const clearFilters = () => {
    setOrigin("");
    setFormat("");
    setLanguage("");
    setAvailability("");
    setQuery("");
  };

  return (
    <div className="site-shell">
      <header className="site-header">
        <a className="wordmark" href="/" aria-label="MuseBooks home">MuseBooks</a>
        <nav className="main-nav" aria-label="Main navigation">
          <a className="active" href="#catalog">Browse the collection</a>
          <a href="#origins">Origins</a>
          <a href="#editions">Editions</a>
          <a href="#collection">Collection</a>
        </nav>
        <div className="header-actions">
          <label className="header-search">
            <Icon name="search" size={18} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search photobooks, titles, or places..." aria-label="Search photobooks" />
          </label>
          <button className="icon-button" onClick={() => toggleSaved(selectedBook?.id || "")} aria-label="Save selected book" aria-pressed={selectedBook ? saved.includes(selectedBook.id) : false}>
            <Icon name="bookmark" size={20} />
          </button>
          <button className="icon-button" aria-label="Account"><Icon name="user" size={20} /></button>
        </div>
        <div className="header-note">Books<br />for a more<br />observant world.</div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <h1>Find the next book worth keeping.</h1>
            <p>Photobooks from Japan, Taiwan, China and Malaysia — different places, shared ways of seeing.</p>
            <form className="hero-search" onSubmit={(event) => event.preventDefault()}>
              <Icon name="search" size={21} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by title, artist, place, or keyword..." aria-label="Search by title, artist, place, or keyword" />
              <button type="submit">Search</button>
            </form>
          </div>
          <div className="hero-botanical" aria-hidden="true">
            <span>More<br />photobooks<br />A kinder<br />world</span>
            <i className="leaf leaf--one" /><i className="leaf leaf--two" /><i className="leaf leaf--three" /><i className="stem" />
          </div>
        </section>

        <section className="catalog-layout" id="catalog">
          <button className="mobile-filter-toggle" onClick={() => setMobileFilters((value) => !value)}>
            {mobileFilters ? "Hide filters" : "Filter the collection"} <Icon name={mobileFilters ? "close" : "chevron"} size={16} />
          </button>
          <aside id="origins" className={"filter-rail" + (mobileFilters ? " filter-rail--open" : "")} aria-label="Catalog filters">
            <div className="filter-heading">
              <h2>Filters</h2>
              <button onClick={clearFilters}>Clear all</button>
            </div>
            <FilterGroup title="Origins">
              {origins.map((item) => (
                <label className="check-row" key={item.code}>
                  <input type="checkbox" checked={origin === item.code} onChange={() => setOrigin(origin === item.code ? "" : item.code)} />
                  <span>{item.name}</span><em>{item.count ?? ""}</em>
                </label>
              ))}
            </FilterGroup>
            <FilterGroup title="Format">
              <label className="check-row"><input type="checkbox" checked={format === "physical"} onChange={() => setFormat(format === "physical" ? "" : "physical")} /><span>Physical book</span><em>89</em></label>
              <label className="check-row"><input type="checkbox" checked={format === "digital"} onChange={() => setFormat(format === "digital" ? "" : "digital")} /><span>Digital edition</span><em>24</em></label>
            </FilterGroup>
            <FilterGroup title="Language">
              {["Japanese", "Traditional Chinese", "Simplified Chinese", "Malay", "English"].map((item) => (
                <label className="check-row" key={item}>
                  <input type="checkbox" checked={language === item} onChange={() => setLanguage(language === item ? "" : item)} />
                  <span>{item}</span><em>{item === "Japanese" ? 32 : item === "Traditional Chinese" ? 28 : item === "Simplified Chinese" ? 18 : item === "Malay" ? 12 : 26}</em>
                </label>
              ))}
            </FilterGroup>
            <FilterGroup title="Availability">
              <label className="check-row"><input type="checkbox" checked={availability === "active"} onChange={() => setAvailability(availability === "active" ? "" : "active")} /><span>In stock</span><em>67</em></label>
              <label className="check-row"><input type="checkbox" checked={availability === "unknown"} onChange={() => setAvailability(availability === "unknown" ? "" : "unknown")} /><span>Pre-order</span><em>14</em></label>
            </FilterGroup>
            <div className="filter-note"><span className="mini-leaf" /><p>A small region.<br /><strong>A wider perspective.</strong></p><span className="dash" /></div>
          </aside>

          <section className="catalog-results" aria-live="polite">
            <div className="results-toolbar">
              <span>{filteredBooks.length ? filteredBooks.length + (filteredBooks.length === 1 ? " book" : " books") : "No books found"}</span>
              <label>Sort by <select defaultValue="featured" aria-label="Sort books"><option value="featured">Featured</option><option value="newest">Newest releases</option><option value="title">Title</option></select></label>
            </div>
            <div className="book-grid">
              {filteredBooks.map((book) => {
                const listingItem = firstListing(book);
                const isSelected = selectedBook?.id === book.id;
                return (
                  <article className={"book-card" + (isSelected ? " book-card--selected" : "")} key={book.id} onClick={() => { setSelectedId(book.id); setSelectedEditionId(book.editions[0]?.id || ""); }}>
                    <div className="book-card__cover"><BookCover book={book} edition={book.editions[0]} /><button className={"card-save" + (saved.includes(book.id) ? " card-save--saved" : "")} onClick={(event) => { event.stopPropagation(); toggleSaved(book.id); }} aria-label={"Save " + (book.englishTitle || book.originalTitle)}><Icon name="bookmark" size={18} /></button></div>
                    <div className="book-card__content">
                      <h3>{book.originalTitle}</h3>
                      <p>{book.englishTitle}</p>
                      <div className="book-card__meta"><span>{book.origin.name}</span><span>{editionFormatLabel(book.editions[0]?.format || "physical")}</span><span>{book.editions[0]?.language}</span></div>
                      <div className="book-card__price">{listingItem ? formatPrice(listingItem.priceMinor, listingItem.currency) : <span className="digital-mark"><Icon name="book" size={14} /> Digital edition</span>}</div>
                    </div>
                  </article>
                );
              })}
            </div>
            {!filteredBooks.length && <div className="empty-state"><Icon name="search" size={24} /><h3>No titles match those filters.</h3><p>Try clearing a filter or searching a wider title, artist, or place.</p><button onClick={clearFilters}>Clear filters</button></div>}
          </section>

          {selectedBook && selectedEdition && (
            <aside id="editions" className="detail-panel" aria-label="Selected photobook">
              <div className="detail-media">
                <BookCover book={selectedBook} edition={selectedEdition} />
                <div className="detail-thumbs">
                  {selectedBook.editions.map((item) => <button key={item.id} className={item.id === selectedEdition.id ? "thumb--selected" : ""} onClick={() => setSelectedEditionId(item.id)} aria-label={"View " + item.editionLabel}><BookCover book={selectedBook} edition={item} compact /></button>)}
                  <button className="more-thumb">+{Math.max(0, selectedBook.editions.length - 1)} more</button>
                </div>
              </div>
              <div className="detail-copy">
                <h2>{selectedBook.originalTitle}</h2>
                <p className="detail-title">{selectedBook.englishTitle}</p>
                <div className="detail-facts">
                  <span><b>Photographer</b>{selectedBook.photographer || "Not recorded"}</span>
                  <span><b>Origin</b>{selectedBook.origin.name}</span>
                  <span><b>Format</b>{editionFormatLabel(selectedEdition.format)}</span>
                  <span><b>Language</b>{selectedEdition.language}</span>
                  <span><b>Pages</b>{selectedEdition.pageCount ? selectedEdition.pageCount + " pages" : "Not recorded"}</span>
                  <span><b>Published</b>{selectedEdition.releaseDate ? new Date(selectedEdition.releaseDate).getFullYear() : "Not recorded"}</span>
                  <span><b>Publisher</b>{selectedEdition.publisher || "Not recorded"}</span>
                  <span><b>Market</b>{selectedEdition.editionMarket || "Not recorded"}</span>
                </div>
                <div className="edition-heading"><h3>Available editions</h3><a href="#editions">View all</a></div>
                <div className="edition-list">
                  {selectedBook.editions.map((item) => {
                    const itemListing = item.listings[0];
                    return <div className={"edition-row" + (item.id === selectedEdition.id ? " edition-row--active" : "")} key={item.id} onClick={() => setSelectedEditionId(item.id)}>
                      <div><strong>{item.editionLabel}</strong><span>{item.format === "digital" ? "Digital edition" : "New"} · {itemListing?.status === "active" ? "In stock" : "Availability unknown"}</span></div>
                      <strong>{itemListing ? formatPrice(itemListing.priceMinor, itemListing.currency) : "View source"}</strong>
                      <a href={itemListing?.url || "#"} target="_blank" rel="noreferrer" onClick={(event) => event.stopPropagation()}>View edition</a>
                    </div>;
                  })}
                </div>
                <div className="detail-actions">
                  {selectedListing && <a href={selectedListing.url} target="_blank" rel="noreferrer"><Icon name="external" size={16} /> Visit source site</a>}
                  <button onClick={() => toggleSaved(selectedBook.id)}><Icon name="bookmark" size={16} /> {saved.includes(selectedBook.id) ? "Saved" : "Add to collection"}</button>
                  <button onClick={shareSelected}><Icon name="share" size={16} /> {shareState === "copied" ? "Link copied" : "Share"}</button>
                </div>
                <div className="detail-quote">“Quiet scenes, lasting memories.”<span>—</span></div>
              </div>
            </aside>
          )}
        </section>
      </main>
      <footer id="collection" className="site-footer"><span>MuseBooks</span><span>Catalog metadata is sourced, time-stamped, and always open to correction.</span><span>{apiState === "live" ? "Connected to catalog API" : "Preview catalog"}</span></footer>
    </div>
  );
}
