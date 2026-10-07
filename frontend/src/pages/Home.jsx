import SeoHead from "../components/SeoHead";
import { usePreferences } from "../lib/preferences";import HeaderControls from "../components/HeaderControls";
import BookDetail from "./BookDetail";
import CatalogPages from "./CatalogPages";
import { useEffect, useMemo, useRef, useState } from "react";
import { apiUrl } from "../lib/api";
import { editionListings, priceLabel, primaryListing, visibleEditions } from "../lib/price-policy";
const isCapacitorBuild = import.meta.env.MODE === "mobile" || import.meta.env.VITE_APP_TARGET === "mobile";
function Icon({ name, size = 18 }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true
  };
  if (name === "search")
  return <svg {...common}><circle cx="11" cy="11" r="6.5" /><path d="m16 16 4.5 4.5" /></svg>;
  if (name === "bookmark")
  return <svg {...common}><path d="M6.5 4.5A1.5 1.5 0 0 1 8 3h8a1.5 1.5 0 0 1 1.5 1.5V21l-5.5-3.2L6.5 21V4.5Z" /></svg>;
  if (name === "chevron")
  return <svg {...common}><path d="m7 9 5 5 5-5" /></svg>;
  if (name === "external")
  return <svg {...common}><path d="M14 5h5v5" /><path d="m19 5-8 8" /><path d="M19 13v4.5A1.5 1.5 0 0 1 17.5 19h-13A1.5 1.5 0 0 1 3 17.5v-13A1.5 1.5 0 0 1 4.5 3H9" /></svg>;
  if (name === "share")
  return <svg {...common}><circle cx="18" cy="5" r="2.2" /><circle cx="6" cy="12" r="2.2" /><circle cx="18" cy="19" r="2.2" /><path d="m8 11 7.8-4.7M8 13l7.8 4.7" /></svg>;
  if (name === "book")
  return <svg {...common}><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H19v17H7.5A2.5 2.5 0 0 0 5 21.5v-17Z" /><path d="M5 4.5v17M8 6h7" /></svg>;
  if (name === "sun")
  return <svg {...common}><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" /></svg>;
  if (name === "moon")
  return <svg {...common}><path d="M20.5 14.2A8.4 8.4 0 0 1 9.8 3.5 8.6 8.6 0 1 0 20.5 14.2Z" /></svg>;
  return <svg {...common}><path d="m6 6 12 12M18 6 6 18" /></svg>;
}

function editionFormatLabel(format) {
  return format === "digital" ? "Digital edition" : "Physical book";
}
function EditionPrices({ edition }) {const { t, formatPrice } = usePreferences();
  const listings = editionListings(edition);
  const groups = edition.format === "digital" ?
  [{ title: "Digital retail prices", items: listings }] :
  [
  { title: "Marketplace active asking prices", items: listings.filter((item) => item.status === "active" && item.priceCategory !== "physical_retail") },
  { title: "Marketplace sold prices", items: listings.filter((item) => item.status === "completed" && item.priceCategory !== "physical_retail") },
  { title: "Physical retailer asking prices", items: listings.filter((item) => item.priceCategory === "physical_retail") }];

  return <section className="price-history" aria-label={edition.format === "digital" ? t("Digital retail offers") : t("Physical marketplace and retailer prices")}>
    {groups.map((group) => <div key={group.title}>
      <div className="edition-heading"><h3>{t(group.title)}</h3></div>
      {!group.items.length && <p className="quiet-state">{t("No records found.")}</p>}
      {group.items.map((item) => <div className="edition-row" key={item.id}>
        <div><strong>{item.source.name}</strong><span>{item.status === "completed" ? t("Completed sale") : item.status === "active" ? t("Available") : item.status === "ended" ? t("Unavailable") : t("Availability unknown")}</span></div>
        <strong>{formatPrice(item.priceMinor, item.currency)}</strong>
        <a href={item.url} target="_blank" rel="noreferrer" data-external-link><Icon name="external" size={14} />{t("View source")}</a>
      </div>)}
    </div>)}
  </section>;
}
function BookCover({ book, edition: selectedEdition, compact = false, loading = "lazy" }) {const { t, formatPrice } = usePreferences();
  const image = selectedEdition?.coverUrl || book.coverUrl;
  return <div className={`cover-art${image ? " cover-art--image" : ""}${compact ? " cover-art--compact" : ""}`}>
    {image && <img src={image} alt="" loading={loading} fetchPriority={loading === "eager" ? "high" : "auto"} />}
    <div className="cover-art__wash" />
    <span className="cover-art__mark">{book.originalTitle.slice(0, 2)}</span>
    <span className="cover-art__title">{book.englishTitle || book.originalTitle}</span>
  </div>;
}
function FilterGroup({ title, children, id }) {const { t, formatPrice } = usePreferences();
  return <section className="filter-group">
    <div className="filter-group__title" id={id}><h3>{t(title)}</h3></div>
    {children}
  </section>;
}
function releaseTimestamp(book) {
  return Math.max(0, ...book.editions.map((item) => item.releaseDate ? Date.parse(item.releaseDate) || 0 : 0));
}
export default function Home() {const { t, formatPrice } = usePreferences();
  const [bookSlug, setBookSlug] = useState(() => {try {return window.location.pathname.startsWith("/books/") ? decodeURIComponent(window.location.pathname.slice(7)) : "";} catch {return "invalid-book";}});
  const [books, setBooks] = useState([]);
  const [origins, setOrigins] = useState([]);
  const [query, setQuery] = useState("");
  const [origin, setOrigin] = useState("");
  const [format, setFormat] = useState("");
  const [availability, setAvailability] = useState("");
  const [selectedId, setSelectedId] = useState("");
  const [selectedEditionId, setSelectedEditionId] = useState("");
  const [saved, setSaved] = useState([]);
  const [shareState, setShareState] = useState("idle");
  const [mobileFilters, setMobileFilters] = useState(false);
  const [activeView, setActiveView] = useState(() => {const route = window.location.pathname.split("/")[1];return ["models", "publishers", "active", "sold"].includes(route) ? route : "browse";});
  const [sortBy, setSortBy] = useState("newest");
  const [apiState, setApiState] = useState("loading");
  const [retry, setRetry] = useState(0);
  const [theme, setTheme] = useState("light");
  const [themeReady, setThemeReady] = useState(false);
  const nativeBackState = useRef({ activeView, mobileFilters, bookSlug });
  nativeBackState.current = { activeView, mobileFilters, bookSlug };
  useEffect(() => {
    try {
      const stored = window.localStorage.getItem("musebooks.collection.v1");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed))
        setSaved(parsed.filter((item) => typeof item === "string"));
      }
      const savedTheme = window.localStorage.getItem("musebooks.theme.v1");
      const initialTheme = savedTheme === "light" || savedTheme === "dark" ?
      savedTheme :
      window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      setTheme(initialTheme);
      document.documentElement.dataset.theme = initialTheme;
    }
    catch {
      document.documentElement.dataset.theme = "light";
    }
    setThemeReady(true);
  }, []);
  useEffect(() => {
    if (!themeReady)
    return;
    document.documentElement.dataset.theme = theme;
    try {
      window.localStorage.setItem("musebooks.theme.v1", theme);
    }
    catch {

      // Theme still applies for this session when browser storage is unavailable.
    }}, [theme, themeReady]);
  useEffect(() => {
    try {
      window.localStorage.setItem("musebooks.collection.v1", JSON.stringify(saved));
    }
    catch {

      // Collection persistence is best effort when browser storage is unavailable.
    }}, [saved]);
  useEffect(() => {
    const controller = new AbortController();
    setApiState("loading");
    Promise.all([
    (async () => {const load = async (page) => {const response = await fetch(apiUrl(`/v1/books?pageSize=50&page=${page}`), { signal: controller.signal });if (!response.ok)
        throw new Error("Catalog unavailable");return response.json();};const first = await load(1);const rest = await Promise.all(Array.from({ length: Math.max(0, first.totalPages - 1) }, (_, index) => load(index + 2)));return { items: [first, ...rest].flatMap((result) => result.items) };})(),
    fetch(apiUrl("/v1/origins"), { signal: controller.signal }).then((response) => response.ok ? response.json() : Promise.reject(response.status))]
    ).
    then(([bookResponse, originResponse]) => {
      if (controller.signal.aborted)
      return;
      setBooks(Array.isArray(bookResponse.items) ? bookResponse.items : []);
      setOrigins(Array.isArray(originResponse) ? originResponse : []);
      setApiState("live");
    }).
    catch(() => {
      if (!controller.signal.aborted)
      setApiState("error");
    });
    return () => controller.abort();
  }, [retry]);
  const filteredBooks = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase();
    const results = books.filter((book) => {
      const haystack = [book.originalTitle, book.englishTitle, book.summary, book.origin.name, book.origin.nativeName, book.origin.code, ...(book.featuredNames || []), book.photographer].
      filter(Boolean).join(" ").toLocaleLowerCase();
      const matchesQuery = !normalized || haystack.includes(normalized);
      const matchesOrigin = !origin || book.origin.code === origin;
      const matchesEdition = visibleEditions(book, { format, availability }).length > 0;
      return matchesQuery && matchesOrigin && matchesEdition;
    });
    if (sortBy === "title")
    return results.sort((a, b) => (a.englishTitle || a.originalTitle).localeCompare(b.englishTitle || b.originalTitle));
    if (sortBy === "newest" || sortBy === "oldest")
    return results.sort((a, b) => {const aDate = releaseTimestamp(a);const bDate = releaseTimestamp(b);if (!aDate || !bDate) return aDate ? -1 : bDate ? 1 : 0;return sortBy === "oldest" ? aDate - bDate : bDate - aDate;});
    return results;
  }, [availability, books, format, origin, query, sortBy]);
  const visibleBooks = activeView === "collection" ? filteredBooks.filter((book) => saved.includes(book.id)) : filteredBooks;
  const selectedBook = bookSlug ? books.find((book) => book.slug === bookSlug) : visibleBooks.find((book) => book.id === selectedId) || visibleBooks[0];
  const selectedEditions = selectedBook ? bookSlug ? selectedBook.editions : visibleEditions(selectedBook, { format, availability }) : [];
  const selectedEdition = selectedEditions.find((item) => item.id === selectedEditionId) || selectedEditions[0];
  const selectedListing = primaryListing(selectedEdition, bookSlug ? "" : availability);
  useEffect(() => {
    if (!books.length)
    return;
    const selectHashBook = () => {
      let slug = "";
      try {
        slug = decodeURIComponent(window.location.hash.slice(1));
      }
      catch {
        return;
      }
      const book = books.find((item) => item.slug === slug);
      if (book) {
        window.history.replaceState(null, "", `/books/${encodeURIComponent(book.slug)}`);
        setBookSlug(book.slug);
        setActiveView("browse");
        setSelectedId(book.id);
        setSelectedEditionId(book.editions[0]?.id || "");
      }
    };
    selectHashBook();
    window.addEventListener("hashchange", selectHashBook);
    return () => window.removeEventListener("hashchange", selectHashBook);
  }, [books]);
  useEffect(() => {
    if (!isCapacitorBuild)
    return;
    const openExternal = (event) => {
      const target = event.target;
      if (!(target instanceof Element))
      return;
      const link = target.closest("a[data-external-link]");
      if (!link)
      return;
      event.preventDefault();
      import("@capacitor/browser").then(({ Browser }) => Browser.open({ url: link.href })).catch(() => window.open(link.href, "_blank", "noopener,noreferrer"));
    };
    document.addEventListener("click", openExternal);
    return () => document.removeEventListener("click", openExternal);
  }, []);
  useEffect(() => {
    if (!isCapacitorBuild)
    return;
    let cancelled = false;
    let removeListener;
    void import("@capacitor/app").
    then(({ App }) => App.addListener("backButton", ({ canGoBack }) => {
      if (nativeBackState.current.bookSlug) {
        if (canGoBack) window.history.back();else
        {setBookSlug("");window.history.replaceState(null, "", "/");}
        return;
      }
      if (nativeBackState.current.mobileFilters) {
        setMobileFilters(false);
        return;
      }
      if (nativeBackState.current.activeView !== "browse") {
        setActiveView("browse");
        return;
      }
      if (canGoBack) {
        window.history.back();
        return;
      }
      App.exitApp();
    })).
    then((handle) => {
      if (cancelled)
      void handle.remove();else

      removeListener = () => {void handle.remove();};
    }).
    catch(() => undefined);
    return () => {
      cancelled = true;
      removeListener?.();
    };
  }, []);
  const toggleSaved = (bookId) => {
    if (!bookId)
    return;
    setSaved((current) => current.includes(bookId) ? current.filter((id) => id !== bookId) : [...current, bookId]);
  };
  const shareSelected = async () => {
    if (!selectedBook)
    return;
    const siteOrigin = isCapacitorBuild ? import.meta.env.VITE_SITE_URL || "https://musebooks.my" : window.location.origin;
    const shareURL = new URL(`/books/${encodeURIComponent(selectedBook.slug)}`, siteOrigin);
    const title = selectedBook.englishTitle || selectedBook.originalTitle;
    try {
      if (isCapacitorBuild) {
        const { Share } = await import("@capacitor/share");
        await Share.share({ title, text: selectedBook.originalTitle, url: shareURL.toString(), dialogTitle: "Share this photobook" });
        setShareState("shared");
      } else
      if (navigator.share) {
        await navigator.share({ title, url: shareURL.toString() });
        setShareState("shared");
      } else
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareURL.toString());
        setShareState("copied");
      } else
      {
        return;
      }
      window.setTimeout(() => setShareState("idle"), 1800);
    }
    catch (error) {
      if (error instanceof Error && error.name === "AbortError")
      return;
      setShareState("idle");
    }
  };
  const clearFilters = () => {
    setOrigin("");
    setFormat("");
    setAvailability("");
    setQuery("");
  };
  useEffect(() => {
    const syncRoute = () => {
      try {setBookSlug(window.location.pathname.startsWith("/books/") ? decodeURIComponent(window.location.pathname.slice(7)) : "");} catch {setBookSlug("invalid-book");}
    };
    window.addEventListener("popstate", syncRoute);
    return () => window.removeEventListener("popstate", syncRoute);
  }, []);

  const navigateView = (view) => {
    setBookSlug("");
    setActiveView(view);
    window.history.pushState(null, "", "/");
  };
  const chooseBook = (book, edition) => {
    window.history.pushState(null, "", `/books/${encodeURIComponent(book.slug)}`);
    setBookSlug(book.slug);
    setSelectedId(book.id);
    setSelectedEditionId(edition?.id || "");
    setShareState("idle");
    window.scrollTo(0, 0);
    window.requestAnimationFrame(() => document.getElementById("book-title")?.focus());
  };
  return <div className={`site-shell${isCapacitorBuild ? " native-mobile-build" : ""}`}>
    <SeoHead path={bookSlug ? `/books/${encodeURIComponent(bookSlug)}` : ["models", "publishers", "active", "sold"].includes(activeView) ? `/${activeView}` : "/"} book={bookSlug ? selectedBook : undefined} noindex={activeView === "collection" || Boolean(window.location.search)} />
    <a className="skip-link" href="#main-content">{t("Skip to catalog")}</a>
    <header className="site-header">
      <a className="wordmark" href="/" aria-label={t("MuseBooks home")}>{t("MuseBooks")}</a>
      <nav className="main-nav" aria-label={t("Main navigation")}>
        <button type="button" className={activeView === "browse" ? "active" : ""} aria-current={activeView === "browse" ? "page" : undefined} onClick={() => navigateView("browse")}>{t("Home")}</button>
        {["models", "publishers", "active", "sold"].map((section) => <a key={section} href={`/${section}`} className={activeView === section ? "active" : ""} aria-current={activeView === section ? "page" : undefined}>{section === "models" ? t("Models") : section === "publishers" ? t("Publishers") : section === "active" ? t("Active listings") : t("Sold listings")}</a>)}
        <button type="button" className={activeView === "collection" ? "active" : ""} aria-current={activeView === "collection" ? "page" : undefined} onClick={() => navigateView("collection")}>{t("Saved collection")}<span className="saved-count">{saved.length}</span></button>
      </nav>
      <HeaderControls theme={theme} setTheme={setTheme} savedCount={saved.length} onCollection={() => navigateView("collection")} />
    </header>

    <main id="main-content">
      {bookSlug ? <>{apiState === "loading" ? <div className="detail-route-state" role="status">{t("Loading photobook\u2026")}</div> : apiState === "error" ? <div className="detail-route-state" role="alert"><h1>{t("This photobook couldn\u2019t be loaded.")}</h1><button onClick={() => setRetry((value) => value + 1)}>{t("Retry connection")}</button></div> : !selectedBook ? <div className="detail-route-state"><h1>{t("Photobook not found.")}</h1><a href="/">{t("Home")}</a></div> : selectedEdition ? <BookDetail {...{ selectedBook, selectedEdition, selectedEditions, selectedListing, availability, saved, shareState, setSelectedEditionId, toggleSaved, shareSelected, BookCover, EditionPrices, Icon, primaryListing, formatPrice, priceLabel, editionFormatLabel }} /> : <div className="detail-route-state"><h1>{selectedBook.originalTitle}</h1><p>{t("No editions recorded yet.")}</p><a href="/">{t("Home")}</a></div>}</> : activeView !== "browse" && activeView !== "collection" ? <CatalogPages key={activeView} section={activeView} /> : <>
      <section className="hero" aria-labelledby="page-title">
        <div className="hero-copy">
          <h1 id="page-title">{t("Find the next book worth keeping.")}</h1>
          <p>{t("Photobooks from Japan, Taiwan, China and Malaysia \u2014 editions and source-backed prices, together.")}</p>
          <form className="hero-search" onSubmit={(event) => {event.preventDefault();document.getElementById("catalog")?.scrollIntoView({ behavior: "smooth", block: "start" });}}>
            <Icon name="search" size={20} />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("Search by title, artist, place, or keyword")} aria-label={t("Search by title, artist, place, or keyword")} />
            <button type="submit">{t("Search")}</button>
          </form>
        </div>
      </section>

      <section className="catalog-layout" id="catalog" aria-label={activeView === "collection" ? t("Saved books") : t("Photobook catalog")}>
        <button className="mobile-filter-toggle" type="button" aria-expanded={mobileFilters} aria-controls="catalog-filter-rail" onClick={() => setMobileFilters((value) => !value)}>
          {mobileFilters ? t("Hide filters") : t("Filter the collection")} <Icon name={mobileFilters ? "close" : "chevron"} size={16} />
        </button>
        <aside id="catalog-filter-rail" className={`filter-rail${mobileFilters ? " filter-rail--open" : ""}`} aria-label={t("Catalog filters")}>
          <div className="filter-heading"><h2>{t("Filters")}</h2><button type="button" onClick={clearFilters}>{t("Clear all")}</button></div>
          <FilterGroup title={t("Origins")} id="origins">
            {origins.map((item) => <label className="check-row" key={item.code}>
              <input type="checkbox" checked={origin === item.code} onChange={() => setOrigin(origin === item.code ? "" : item.code)} />
              <span>{t(item.name)}</span>{item.count !== undefined && <em>{item.count}</em>}
            </label>)}
          </FilterGroup>
          <FilterGroup title={t("Format")}>
            <label className="check-row"><input type="checkbox" checked={format === "physical"} onChange={() => setFormat(format === "physical" ? "" : "physical")} /><span>{t("Physical book")}</span></label>
            <label className="check-row"><input type="checkbox" checked={format === "digital"} onChange={() => {setFormat(format === "digital" ? "" : "digital");if (availability === "completed")
                  setAvailability("");}} /><span>{t("Digital edition")}</span></label>
          </FilterGroup>
          <FilterGroup title={t("Availability")}>
            <label className="check-row"><input type="checkbox" checked={availability === "active"} onChange={() => setAvailability(availability === "active" ? "" : "active")} /><span>{t("In stock")}</span></label>
            <label className="check-row"><input type="checkbox" checked={availability === "unknown"} onChange={() => setAvailability(availability === "unknown" ? "" : "unknown")} /><span>{t("Availability unknown")}</span></label>
            <label className="check-row"><input type="checkbox" disabled={format === "digital"} checked={availability === "completed"} onChange={() => setAvailability(availability === "completed" ? "" : "completed")} /><span>{t("Sold (physical)")}</span></label>
          </FilterGroup>
          <div className="filter-note"><Icon name="book" size={20} /><p>{t("Every edition has its own record.")}<br /><strong>{t("Prices keep their source context.")}</strong></p></div>
        </aside>

        <section className="catalog-results" aria-label={activeView === "collection" ? t("Saved photobooks") : t("Catalog results")}>
          <div className="results-toolbar">
            <span className="results-count" role="status">{apiState === "loading" ? t("Loading catalog") : activeView === "collection" ? t(`${visibleBooks.length} saved ${visibleBooks.length === 1 ? "book" : "books"}`) : t(`${visibleBooks.length} ${visibleBooks.length === 1 ? "book" : "books"}`)}</span>
            <label>{t("Sort by")}<select value={sortBy} onChange={(event) => setSortBy(event.target.value)} aria-label={t("Sort books")}>
              <option value="newest">{t("Newest release")}</option><option value="oldest">{t("Oldest release")}</option><option value="title">{t("Title")}</option>
            </select></label>
          </div>
          {apiState === "error" && <div className="catalog-message" role="alert"><div><strong>{t("The catalog couldn\u2019t be reached.")}</strong><span>{t("Check your connection and retry. No sample books are shown.")}</span></div><button type="button" onClick={() => setRetry((value) => value + 1)}>{t("Retry")}</button></div>}
          {apiState === "loading" && <div className="book-grid book-grid--loading" role="status" aria-label={t("Loading photobooks")}><span className="visually-hidden">{t("Loading photobooks\u2026")}</span>{[0, 1, 2, 3, 4, 5].map((item) => <div className="book-skeleton" key={item}><span /><i /><i /></div>)}</div>}
          {apiState === "live" && visibleBooks.length > 0 && <div className="book-grid">
            {visibleBooks.map((book, index) => {
                const cardEdition = visibleEditions(book, { format, availability })[0];
                const listingItem = primaryListing(cardEdition, availability);
                return <article className="book-card" key={book.id}>
                <a className="book-card__select" href={`/books/${encodeURIComponent(book.slug)}`} onClick={(event) => {if (event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey) {event.preventDefault();chooseBook(book, cardEdition);}}} aria-label={`Show details for ${book.englishTitle || book.originalTitle}`}>
                  <div className="book-card__cover"><BookCover book={book} edition={cardEdition} loading={index < 3 ? "eager" : "lazy"} /></div>
                  <div className="book-card__content">
                    <h3>{book.originalTitle}</h3>
                    {book.englishTitle && <p>{book.englishTitle}</p>}
                    <div className="book-card__meta"><span>{t(book.origin.name)}</span><span>{cardEdition ? t(editionFormatLabel(cardEdition.format)) : t("No edition recorded")}</span></div>
                    <div className="book-card__price">{listingItem ? formatPrice(listingItem.priceMinor, listingItem.currency) : cardEdition ? t("Price not recorded") : t("No edition record")}</div>
                    <div className="book-card__meta"><span>{cardEdition ? t(priceLabel(cardEdition, listingItem)) : t("No source-backed edition yet")}</span></div>
                  </div>
                </a>
                <button className={`card-save${saved.includes(book.id) ? " card-save--saved" : ""}`} type="button" onClick={() => toggleSaved(book.id)} aria-label={`${saved.includes(book.id) ? t("Remove") : t("Save")} ${book.englishTitle || book.originalTitle}`} aria-pressed={saved.includes(book.id)}>
                  <Icon name="bookmark" size={18} />
                </button>
              </article>;
              })}
          </div>}
          {apiState === "live" && visibleBooks.length === 0 && <div className="empty-state">
            <Icon name={activeView === "collection" ? "bookmark" : "search"} size={24} />
            <h3>{activeView === "collection" && saved.length === 0 ? t("Your collection is ready.") : activeView === "collection" ? t("No saved books match.") : t("No titles match those filters.")}</h3>
            <p>{activeView === "collection" && saved.length === 0 ? t("Save a photobook to keep its editions and source prices close.") : t("Try clearing a filter or searching a wider title, artist, or place.")}</p>
            {activeView === "collection" && saved.length === 0 ?
              <button type="button" onClick={() => navigateView("browse")}>{t("Browse the catalog")}</button> :
              <button type="button" onClick={clearFilters}>{t("Clear filters")}</button>}
          </div>}
        </section>


      </section>
      </>}
    </main>

    <footer className="site-footer"><span>{t("MuseBooks")}</span><span>{t("Listings keep their source, format, and availability context.")}</span><a href="/privacy-policy">{t("Privacy Policy")}</a><span className={`connection-status connection-status--${apiState}`}>{apiState === "live" ? t("Catalog connected") : apiState === "loading" ? t("Connecting to catalog") : t("Catalog unavailable")}</span></footer>

    {isCapacitorBuild && <nav className="mobile-tabbar" aria-label={t("App navigation")}>
      <button type="button" className={activeView === "browse" ? "is-active" : ""} aria-current={activeView === "browse" ? "page" : undefined} onClick={() => navigateView("browse")}><Icon name="book" size={20} /><span>{t("Browse")}</span></button>
      <button type="button" className={activeView === "collection" ? "is-active" : ""} aria-current={activeView === "collection" ? "page" : undefined} onClick={() => navigateView("collection")}><Icon name="bookmark" size={20} /><span>{t("Collection")}</span><i>{saved.length}</i></button>
    </nav>}
  </div>;
}
