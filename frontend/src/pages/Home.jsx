import CatalogPages from "./CatalogPages";
import { useEffect, useMemo, useRef, useState } from "react";
import { apiUrl } from "../lib/api";
import { editionListings, formatPrice, priceLabel, primaryListing, visibleEditions } from "../lib/price-policy";
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
        "aria-hidden": true,
    };
    if (name === "search")
        return <svg {...common}><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>;
    if (name === "bookmark")
        return <svg {...common}><path d="M6.5 4.5A1.5 1.5 0 0 1 8 3h8a1.5 1.5 0 0 1 1.5 1.5V21l-5.5-3.2L6.5 21V4.5Z"/></svg>;
    if (name === "chevron")
        return <svg {...common}><path d="m7 9 5 5 5-5"/></svg>;
    if (name === "external")
        return <svg {...common}><path d="M14 5h5v5"/><path d="m19 5-8 8"/><path d="M19 13v4.5A1.5 1.5 0 0 1 17.5 19h-13A1.5 1.5 0 0 1 3 17.5v-13A1.5 1.5 0 0 1 4.5 3H9"/></svg>;
    if (name === "share")
        return <svg {...common}><circle cx="18" cy="5" r="2.2"/><circle cx="6" cy="12" r="2.2"/><circle cx="18" cy="19" r="2.2"/><path d="m8 11 7.8-4.7M8 13l7.8 4.7"/></svg>;
    if (name === "book")
        return <svg {...common}><path d="M5 4.5A2.5 2.5 0 0 1 7.5 2H19v17H7.5A2.5 2.5 0 0 0 5 21.5v-17Z"/><path d="M5 4.5v17M8 6h7"/></svg>;
    if (name === "sun")
        return <svg {...common}><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></svg>;
    if (name === "moon")
        return <svg {...common}><path d="M20.5 14.2A8.4 8.4 0 0 1 9.8 3.5 8.6 8.6 0 1 0 20.5 14.2Z"/></svg>;
    return <svg {...common}><path d="m6 6 12 12M18 6 6 18"/></svg>;
}
function editionFormatLabel(format) {
    return format === "digital" ? "Digital edition" : "Physical book";
}
function EditionPrices({ edition }) {
    const listings = editionListings(edition);
    const groups = edition.format === "digital"
        ? [{ title: "Digital retail prices", items: listings }]
        : [
            { title: "Marketplace active asking prices", items: listings.filter((item) => item.status === "active" && item.priceCategory !== "physical_retail") },
            { title: "Marketplace sold prices", items: listings.filter((item) => item.status === "completed" && item.priceCategory !== "physical_retail") },
            { title: "Physical retailer asking prices", items: listings.filter((item) => item.priceCategory === "physical_retail") },
        ];
    return <section className="price-history" aria-label={edition.format === "digital" ? "Digital retail offers" : "Physical marketplace and retailer prices"}>
    {groups.map((group) => <div key={group.title}>
      <div className="edition-heading"><h3>{group.title}</h3></div>
      {!group.items.length && <p className="quiet-state">No records found.</p>}
      {group.items.map((item) => <div className="edition-row" key={item.id}>
        <div><strong>{item.source.name}</strong><span>{item.status === "completed" ? "Completed sale" : item.status === "active" ? "Available" : item.status === "ended" ? "Unavailable" : "Availability unknown"}</span></div>
        <strong>{formatPrice(item.priceMinor, item.currency)}</strong>
        <a href={item.url} target="_blank" rel="noreferrer" data-external-link><Icon name="external" size={14}/> View source</a>
      </div>)}
    </div>)}
  </section>;
}
function BookCover({ book, edition: selectedEdition, compact = false, loading = "lazy", }) {
    const image = selectedEdition?.coverUrl || book.coverUrl;
    return <div className={`cover-art${compact ? " cover-art--compact" : ""}`}>
    {image && <img src={image} alt="" loading={loading} fetchPriority={loading === "eager" ? "high" : "auto"}/>}
    <div className="cover-art__wash"/>
    <span className="cover-art__mark">{book.originalTitle.slice(0, 2)}</span>
    <span className="cover-art__title">{book.englishTitle || book.originalTitle}</span>
  </div>;
}
function FilterGroup({ title, children, id }) {
    return <section className="filter-group">
    <div className="filter-group__title" id={id}><h3>{title}</h3></div>
    {children}
  </section>;
}
function releaseTimestamp(book) {
    return Math.max(0, ...book.editions.map((item) => item.releaseDate ? Date.parse(item.releaseDate) || 0 : 0));
}
export default function Home() {
    const [books, setBooks] = useState([]);
    const [origins, setOrigins] = useState([]);
    const [query, setQuery] = useState("");
    const [origin, setOrigin] = useState("");
    const [format, setFormat] = useState("");
    const [language, setLanguage] = useState("");
    const [availability, setAvailability] = useState("");
    const [selectedId, setSelectedId] = useState("");
    const [selectedEditionId, setSelectedEditionId] = useState("");
    const [saved, setSaved] = useState([]);
    const [shareState, setShareState] = useState("idle");
    const [mobileFilters, setMobileFilters] = useState(false);
    const [activeView, setActiveView] = useState(() => { const route = window.location.pathname.split("/")[1]; return ["models", "publishers", "active", "sold"].includes(route) ? route : "browse"; });
    const [sortBy, setSortBy] = useState("featured");
    const [apiState, setApiState] = useState("loading");
    const [retry, setRetry] = useState(0);
    const [theme, setTheme] = useState("light");
    const [themeReady, setThemeReady] = useState(false);
    const nativeBackState = useRef({ activeView, mobileFilters });
    nativeBackState.current = { activeView, mobileFilters };
    useEffect(() => {
        try {
            const stored = window.localStorage.getItem("musebooks.collection.v1");
            if (stored) {
                const parsed = JSON.parse(stored);
                if (Array.isArray(parsed))
                    setSaved(parsed.filter((item) => typeof item === "string"));
            }
            const savedTheme = window.localStorage.getItem("musebooks.theme.v1");
            const initialTheme = savedTheme === "light" || savedTheme === "dark"
                ? savedTheme
                : window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
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
        }
    }, [theme, themeReady]);
    useEffect(() => {
        try {
            window.localStorage.setItem("musebooks.collection.v1", JSON.stringify(saved));
        }
        catch {
            // Collection persistence is best effort when browser storage is unavailable.
        }
    }, [saved]);
    useEffect(() => {
        const controller = new AbortController();
        setApiState("loading");
        Promise.all([
            (async () => { const load = async (page) => { const response = await fetch(apiUrl(`/v1/books?pageSize=50&page=${page}`), { signal: controller.signal }); if (!response.ok)
                throw new Error("Catalog unavailable"); return response.json(); }; const first = await load(1); const rest = await Promise.all(Array.from({ length: Math.max(0, first.totalPages - 1) }, (_, index) => load(index + 2))); return { items: [first, ...rest].flatMap(result => result.items) }; })(),
            fetch(apiUrl("/v1/origins"), { signal: controller.signal }).then((response) => response.ok ? response.json() : Promise.reject(response.status)),
        ])
            .then(([bookResponse, originResponse]) => {
            if (controller.signal.aborted)
                return;
            setBooks(Array.isArray(bookResponse.items) ? bookResponse.items : []);
            setOrigins(Array.isArray(originResponse) ? originResponse : []);
            setApiState("live");
        })
            .catch(() => {
            if (!controller.signal.aborted)
                setApiState("error");
        });
        return () => controller.abort();
    }, [retry]);
    const filteredBooks = useMemo(() => {
        const normalized = query.trim().toLocaleLowerCase();
        const results = books.filter((book) => {
            const haystack = [book.originalTitle, book.englishTitle, book.summary, book.origin.name, book.origin.nativeName, book.origin.code, ...(book.featuredNames || []), book.photographer]
                .filter(Boolean).join(" ").toLocaleLowerCase();
            const matchesQuery = !normalized || haystack.includes(normalized);
            const matchesOrigin = !origin || book.origin.code === origin;
            const matchesEdition = visibleEditions(book, { format, language, availability }).length > 0;
            return matchesQuery && matchesOrigin && matchesEdition;
        });
        if (sortBy === "title")
            return results.sort((a, b) => (a.englishTitle || a.originalTitle).localeCompare(b.englishTitle || b.originalTitle));
        if (sortBy === "newest")
            return results.sort((a, b) => releaseTimestamp(b) - releaseTimestamp(a));
        return results;
    }, [availability, books, format, language, origin, query, sortBy]);
    const languages = useMemo(() => Array.from(new Set(books.flatMap((book) => (book.editions || []).map((edition) => edition.language).filter((value) => Boolean(value))))).sort((a, b) => a.localeCompare(b)), [books]);
    const visibleBooks = activeView === "collection" ? filteredBooks.filter((book) => saved.includes(book.id)) : filteredBooks;
    const selectedBook = visibleBooks.find((book) => book.id === selectedId) || visibleBooks[0];
    const selectedEditions = selectedBook ? visibleEditions(selectedBook, { format, language, availability }) : [];
    const selectedEdition = selectedEditions.find((item) => item.id === selectedEditionId) || selectedEditions[0];
    const selectedListing = primaryListing(selectedEdition, availability);
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
        void import("@capacitor/app")
            .then(({ App }) => App.addListener("backButton", ({ canGoBack }) => {
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
        }))
            .then((handle) => {
            if (cancelled)
                void handle.remove();
            else
                removeListener = () => { void handle.remove(); };
        })
            .catch(() => undefined);
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
        const shareURL = new URL("/", siteOrigin);
        shareURL.hash = selectedBook.slug;
        const title = selectedBook.englishTitle || selectedBook.originalTitle;
        try {
            if (isCapacitorBuild) {
                const { Share } = await import("@capacitor/share");
                await Share.share({ title, text: selectedBook.originalTitle, url: shareURL.toString(), dialogTitle: "Share this photobook" });
                setShareState("shared");
            }
            else if (navigator.share) {
                await navigator.share({ title, url: shareURL.toString() });
                setShareState("shared");
            }
            else if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(shareURL.toString());
                setShareState("copied");
            }
            else {
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
        setLanguage("");
        setAvailability("");
        setQuery("");
    };
    const chooseBook = (book, edition) => {
        setSelectedId(book.id);
        setSelectedEditionId(edition?.id || "");
    };
    return <div className={`site-shell${isCapacitorBuild ? " native-mobile-build" : ""}`}>
    <a className="skip-link" href="#main-content">Skip to catalog</a>
    <header className="site-header">
      <a className="wordmark" href="/" aria-label="MuseBooks home">MuseBooks</a>
      <nav className="main-nav" aria-label="Main navigation">
        <button type="button" className={activeView === "browse" ? "active" : ""} aria-current={activeView === "browse" ? "page" : undefined} onClick={() => setActiveView("browse")}>Browse the collection</button>
        {["models", "publishers", "active", "sold"].map(section => <a key={section} href={`/${section}`} className={activeView === section ? "active" : ""} aria-current={activeView === section ? "page" : undefined}>{section === "models" ? "Models" : section === "publishers" ? "Publishers" : section === "active" ? "Active listings" : "Sold listings"}</a>)}
        <button type="button" className={activeView === "collection" ? "active" : ""} aria-current={activeView === "collection" ? "page" : undefined} onClick={() => setActiveView("collection")}>Saved collection <span className="saved-count">{saved.length}</span></button>
      </nav>
      <div className="header-actions">
        {(activeView === "browse" || activeView === "collection") && <label className="header-search">
          <Icon name="search" size={18}/>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search photobooks, titles, or places" aria-label="Search photobooks"/>
        </label>}
        <button className="icon-button" type="button" onClick={() => setTheme((value) => value === "light" ? "dark" : "light")} aria-label={`Switch to ${theme === "light" ? "dark" : "light"} appearance`} title={`Switch to ${theme === "light" ? "dark" : "light"} appearance`}>
          <Icon name={theme === "light" ? "moon" : "sun"} size={20}/>
        </button>
        <button className="icon-button" type="button" onClick={() => setActiveView("collection")} aria-label={`Open saved collection, ${saved.length} saved`} aria-pressed={activeView === "collection"}>
          <Icon name="bookmark" size={20}/>
        </button>
      </div>
    </header>

    <main id="main-content">
      {activeView !== "browse" && activeView !== "collection" ? <CatalogPages key={activeView} section={activeView}/> : <>
      <section className="hero" aria-labelledby="page-title">
        <div className="hero-copy">
          <h1 id="page-title">Find the next book worth keeping.</h1>
          <p>Photobooks from Japan, Taiwan, China and Malaysia — editions and source-backed prices, together.</p>
          <form className="hero-search" onSubmit={(event) => { event.preventDefault(); document.getElementById("catalog")?.scrollIntoView({ behavior: "smooth", block: "start" }); }}>
            <Icon name="search" size={20}/>
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by title, artist, place, or keyword" aria-label="Search by title, artist, place, or keyword"/>
            <button type="submit">Search</button>
          </form>
        </div>
        <div className="hero-record" aria-label={selectedBook ? `Featured record: ${selectedBook.englishTitle || selectedBook.originalTitle}` : "Catalog connection status"}>
          {selectedBook && selectedEdition ? <>
            <BookCover book={selectedBook} edition={selectedEdition} loading="eager"/>
            <div className="hero-record__caption"><span>{selectedBook.origin.nativeName || selectedBook.origin.name}</span><strong>{selectedBook.englishTitle || selectedBook.originalTitle}</strong></div>
          </> : <div className={`hero-record__state hero-record__state--${apiState}`} role="status">
            <Icon name="book" size={24}/>
            <strong>{apiState === "loading" ? "Opening the catalog" : apiState === "error" ? "Catalog connection unavailable" : selectedBook ? "No edition records to show" : "No books match these filters"}</strong>
            {apiState === "error" && <button type="button" onClick={() => setRetry((value) => value + 1)}>Retry connection</button>}
          </div>}
        </div>
      </section>

      {selectedBook && selectedEdition && <section className="provenance-strip" aria-label="Selected book provenance">
        <div><span>Work</span><strong>{selectedBook.origin.name}</strong></div>
        <div><span>Edition</span><strong>{selectedEdition.editionLabel}</strong></div>
        <div><span>Format</span><strong>{editionFormatLabel(selectedEdition.format)}</strong></div>
        <div><span>Price context</span><strong>{priceLabel(selectedEdition, selectedListing)}</strong></div>
      </section>}

      <section className="catalog-layout" id="catalog" aria-label={activeView === "collection" ? "Saved books" : "Photobook catalog"}>
        <button className="mobile-filter-toggle" type="button" aria-expanded={mobileFilters} aria-controls="catalog-filter-rail" onClick={() => setMobileFilters((value) => !value)}>
          {mobileFilters ? "Hide filters" : "Filter the collection"} <Icon name={mobileFilters ? "close" : "chevron"} size={16}/>
        </button>
        <aside id="catalog-filter-rail" className={`filter-rail${mobileFilters ? " filter-rail--open" : ""}`} aria-label="Catalog filters">
          <div className="filter-heading"><h2>Filters</h2><button type="button" onClick={clearFilters}>Clear all</button></div>
          <FilterGroup title="Origins" id="origins">
            {origins.map((item) => <label className="check-row" key={item.code}>
              <input type="checkbox" checked={origin === item.code} onChange={() => setOrigin(origin === item.code ? "" : item.code)}/>
              <span>{item.name}</span>{item.count !== undefined && <em>{item.count}</em>}
            </label>)}
          </FilterGroup>
          <FilterGroup title="Format">
            <label className="check-row"><input type="checkbox" checked={format === "physical"} onChange={() => setFormat(format === "physical" ? "" : "physical")}/><span>Physical book</span></label>
            <label className="check-row"><input type="checkbox" checked={format === "digital"} onChange={() => { setFormat(format === "digital" ? "" : "digital"); if (availability === "completed")
            setAvailability(""); }}/><span>Digital edition</span></label>
          </FilterGroup>
          <FilterGroup title="Language">
            {languages.map((item) => <label className="check-row" key={item}>
              <input type="checkbox" checked={language === item} onChange={() => setLanguage(language === item ? "" : item)}/><span>{item}</span>
            </label>)}
            {!languages.length && <span className="quiet-state">No languages recorded.</span>}
          </FilterGroup>
          <FilterGroup title="Availability">
            <label className="check-row"><input type="checkbox" checked={availability === "active"} onChange={() => setAvailability(availability === "active" ? "" : "active")}/><span>In stock</span></label>
            <label className="check-row"><input type="checkbox" checked={availability === "unknown"} onChange={() => setAvailability(availability === "unknown" ? "" : "unknown")}/><span>Availability unknown</span></label>
            <label className="check-row"><input type="checkbox" disabled={format === "digital"} checked={availability === "completed"} onChange={() => setAvailability(availability === "completed" ? "" : "completed")}/><span>Sold (physical)</span></label>
          </FilterGroup>
          <div className="filter-note"><Icon name="book" size={20}/><p>Every edition has its own record.<br /><strong>Prices keep their source context.</strong></p></div>
        </aside>

        <section className="catalog-results" aria-label={activeView === "collection" ? "Saved photobooks" : "Catalog results"}>
          <div className="results-toolbar">
            <span className="results-count" role="status">{apiState === "loading" ? "Loading catalog" : activeView === "collection" ? `${visibleBooks.length} saved ${visibleBooks.length === 1 ? "book" : "books"}` : `${visibleBooks.length} ${visibleBooks.length === 1 ? "book" : "books"}`}</span>
            <label>Sort by <select value={sortBy} onChange={(event) => setSortBy(event.target.value)} aria-label="Sort books">
              <option value="featured">Catalog order</option><option value="newest">Newest releases</option><option value="title">Title</option>
            </select></label>
          </div>
          {apiState === "error" && <div className="catalog-message" role="alert"><div><strong>The catalog couldn’t be reached.</strong><span>Check your connection and retry. No sample books are shown.</span></div><button type="button" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>}
          {apiState === "loading" && <div className="book-grid book-grid--loading" role="status" aria-label="Loading photobooks"><span className="visually-hidden">Loading photobooks…</span>{[0, 1, 2, 3, 4, 5].map((item) => <div className="book-skeleton" key={item}><span /><i /><i /></div>)}</div>}
          {apiState === "live" && visibleBooks.length > 0 && <div className="book-grid">
            {visibleBooks.map((book, index) => {
                    const cardEdition = visibleEditions(book, { format, language, availability })[0];
                    const listingItem = primaryListing(cardEdition, availability);
                    const isSelected = selectedBook?.id === book.id;
                    return <article className={`book-card${isSelected ? " book-card--selected" : ""}`} key={book.id}>
                <button className="book-card__select" type="button" onClick={() => chooseBook(book, cardEdition)} aria-pressed={isSelected} aria-label={`Show details for ${book.englishTitle || book.originalTitle}`}>
                  <div className="book-card__cover"><BookCover book={book} edition={cardEdition} loading={index < 3 ? "eager" : "lazy"}/></div>
                  <div className="book-card__content">
                    <h3>{book.originalTitle}</h3>
                    {book.englishTitle && <p>{book.englishTitle}</p>}
                    <div className="book-card__meta"><span>{book.origin.name}</span><span>{cardEdition ? editionFormatLabel(cardEdition.format) : "No edition recorded"}</span></div>
                    <div className="book-card__price">{listingItem ? formatPrice(listingItem.priceMinor, listingItem.currency) : cardEdition ? "Price not recorded" : "No edition record"}</div>
                    <div className="book-card__meta"><span>{cardEdition ? priceLabel(cardEdition, listingItem) : "No source-backed edition yet"}</span></div>
                  </div>
                </button>
                <button className={`card-save${saved.includes(book.id) ? " card-save--saved" : ""}`} type="button" onClick={() => toggleSaved(book.id)} aria-label={`${saved.includes(book.id) ? "Remove" : "Save"} ${book.englishTitle || book.originalTitle}`} aria-pressed={saved.includes(book.id)}>
                  <Icon name="bookmark" size={18}/>
                </button>
              </article>;
                })}
          </div>}
          {apiState === "live" && visibleBooks.length === 0 && <div className="empty-state">
            <Icon name={activeView === "collection" ? "bookmark" : "search"} size={24}/>
            <h3>{activeView === "collection" && saved.length === 0 ? "Your collection is ready." : activeView === "collection" ? "No saved books match." : "No titles match those filters."}</h3>
            <p>{activeView === "collection" && saved.length === 0 ? "Save a photobook to keep its editions and source prices close." : "Try clearing a filter or searching a wider title, artist, or place."}</p>
            {activeView === "collection" && saved.length === 0
                    ? <button type="button" onClick={() => setActiveView("browse")}>Browse the catalog</button>
                    : <button type="button" onClick={clearFilters}>Clear filters</button>}
          </div>}
        </section>

        {selectedBook && selectedEdition && <aside id="editions" className="detail-panel" aria-label="Selected photobook">
          <div className="detail-media">
            <BookCover book={selectedBook} edition={selectedEdition} loading="eager"/>
            <div className="detail-thumbs">
              {selectedBook.editions.map((item) => <button key={item.id} type="button" className={item.id === selectedEdition.id ? "thumb--selected" : ""} onClick={() => setSelectedEditionId(item.id)} aria-label={`View ${item.editionLabel}`} aria-pressed={item.id === selectedEdition.id}><BookCover book={selectedBook} edition={item} compact/></button>)}
              {selectedBook.editions.length > 1 && <a className="more-thumb" href="#available-editions">All editions</a>}
            </div>
          </div>
          <div className="detail-copy">
            <h2>{selectedBook.originalTitle}</h2>
            {selectedBook.englishTitle && <p className="detail-title">{selectedBook.englishTitle}</p>}
            <div className="detail-facts">
              <span><b>Photographer</b>{selectedBook.photographer || "Not recorded"}</span>
              <span><b>Origin</b>{selectedBook.origin.name}</span>
              <span><b>Format</b>{editionFormatLabel(selectedEdition.format)}</span>
              <span><b>Language</b>{selectedEdition.language || "Not recorded"}</span>
              <span><b>Pages</b>{selectedEdition.pageCount ? `${selectedEdition.pageCount} pages` : "Not recorded"}</span>
              <span><b>Published</b>{selectedEdition.releaseDate ? new Date(selectedEdition.releaseDate).getFullYear() : "Not recorded"}</span>
              <span><b>Publisher</b>{selectedEdition.publisher || "Not recorded"}</span>
              <span><b>Market</b>{selectedEdition.editionMarket || "Not recorded"}</span>
            </div>
            <div className="edition-heading" id="available-editions"><h3>Available editions</h3><a href="#edition-list">View all</a></div>
            <div className="edition-list" id="edition-list">
              {selectedEditions.map((item) => {
                    const itemListing = primaryListing(item, availability);
                    const active = item.id === selectedEdition.id;
                    return <div className={`edition-row${active ? " edition-row--active" : ""}`} key={item.id}>
                  <button className="edition-row__select" type="button" onClick={() => setSelectedEditionId(item.id)} aria-pressed={active}>
                    <strong>{item.editionLabel}</strong><span>{editionFormatLabel(item.format)} · {priceLabel(item, itemListing)}</span>
                  </button>
                  <strong>{itemListing ? formatPrice(itemListing.priceMinor, itemListing.currency) : "No price"}</strong>
                  {itemListing?.url ? <a href={itemListing.url} target="_blank" rel="noreferrer" data-external-link>View source</a> : <span className="quiet-state">No source</span>}
                </div>;
                })}
            </div>
            <EditionPrices edition={selectedEdition}/>
            <div className="detail-actions">
              {selectedListing && <a className="action-primary" href={selectedListing.url} target="_blank" rel="noreferrer" data-external-link><Icon name="external" size={16}/> Visit source site</a>}
              <button type="button" onClick={() => toggleSaved(selectedBook.id)} aria-pressed={saved.includes(selectedBook.id)}><Icon name="bookmark" size={16}/> {saved.includes(selectedBook.id) ? "Saved to collection" : "Save to collection"}</button>
              <button type="button" onClick={shareSelected}><Icon name="share" size={16}/> {shareState === "shared" ? "Share sheet opened" : shareState === "copied" ? "Link copied" : "Share"}</button>
            </div>
          </div>
        </aside>}
      </section>
      </>}
    </main>

    <footer className="site-footer"><span>MuseBooks</span><span>Listings keep their source, format, and availability context.</span><a href="/privacy-policy">Privacy Policy</a><span className={`connection-status connection-status--${apiState}`}>{apiState === "live" ? "Catalog connected" : apiState === "loading" ? "Connecting to catalog" : "Catalog unavailable"}</span></footer>

    {isCapacitorBuild && <nav className="mobile-tabbar" aria-label="App navigation">
      <button type="button" className={activeView === "browse" ? "is-active" : ""} aria-current={activeView === "browse" ? "page" : undefined} onClick={() => setActiveView("browse")}><Icon name="book" size={20}/><span>Browse</span></button>
      <button type="button" className={activeView === "collection" ? "is-active" : ""} aria-current={activeView === "collection" ? "page" : undefined} onClick={() => setActiveView("collection")}><Icon name="bookmark" size={20}/><span>Collection</span><i>{saved.length}</i></button>
    </nav>}
  </div>;
}
