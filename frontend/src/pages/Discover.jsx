import { useMemo, useState } from "react";
import SeoHead from "../components/SeoHead";
import Icon from "../components/Icon";
import BookCard, { BookGridSkeleton } from "../components/BookCard";
import { LoadState, SectionHeading } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { useCollection } from "../lib/collection";
import { showCatalogImages } from "../lib/platform";
import { navigate } from "../lib/router";
import { loadAllBooks, loadModelTotal, loadOrigins, photobookModels, sortBooks, useLoader, useResource } from "../lib/catalog";

function MarketList({ status, title, href }) {
  const { t, formatPrice } = usePreferences();
  const listings = useResource(`/v1/listings?status=${status}&pageSize=6&page=1`);
  return <section className="market-pulse__column" aria-labelledby={`pulse-${status}`}>
    <SectionHeading id={`pulse-${status}`} title={t(title)} action={t("See all")} href={href} />
    <LoadState state={listings.state} retry={listings.retry} empty={listings.state === "live" && !listings.data.items.length} emptyMessage="No listings recorded yet." />
    {listings.state === "live" && <ol className="pulse-list">
      {listings.data.items.map(item => <li key={item.id}>
        <a href={`/books/${encodeURIComponent(item.workSlug)}`}>
          <span className="pulse-list__title">{item.workTitle}<small>{item.source?.name}{item.editionLabel ? ` · ${item.editionLabel}` : ""}</small></span>
          <strong>{formatPrice(item.priceMinor, item.currency)}</strong>
        </a>
      </li>)}
    </ol>}
  </section>;
}

export default function Discover() {
  const { t } = usePreferences();
  const { saved } = useCollection();
  const [query, setQuery] = useState("");
  const books = useLoader(loadAllBooks, []);
  const origins = useLoader(loadOrigins, []);
  const modelTotal = useLoader(loadModelTotal, []);
  const newest = useMemo(() => books.state === "live" ? sortBooks(books.data, "newest").slice(0, 8) : [], [books.state, books.data]);
  const savedBooks = useMemo(() => books.state === "live" ? books.data.filter(book => saved.includes(book.id)).slice(0, 4) : [], [books.state, books.data, saved]);
  const featuredModels = useMemo(() => books.state === "live" ? photobookModels(books.data).slice(0, 8) : [], [books.state, books.data]);
  const editionCount = books.state === "live" ? books.data.reduce((sum, book) => sum + (book.editions?.length || 0), 0) : null;
  return <>
    <SeoHead path="/" />
    <section className="hero" aria-labelledby="page-title">
      <div className="page-width hero__inner">
        <p className="eyebrow">{t("Photobooks · Magazine issues · Editions · Prices")}</p>
        <h1 id="page-title">{t("Find the next publication worth keeping.")}</h1>
        <p className="hero__intro">{t("Photobooks and magazine issues from Japan, Taiwan, China, Malaysia, and Korea — with editions and source-backed prices.")}</p>
        <form className="search-field search-field--hero" role="search" onSubmit={event => { event.preventDefault(); navigate(`/books${query.trim() ? `?q=${encodeURIComponent(query.trim())}` : ""}`); }}>
          <Icon name="search" size={20} />
          <input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder={t("Search by title, model, or publisher")} aria-label={t("Search the catalog")} />
          <button type="submit" className="button">{t("Search")}</button>
        </form>
        {books.state === "live" && <dl className="hero__stats">
          <div><dt>{t("Publications")}</dt><dd>{books.data.length.toLocaleString()}</dd></div>
          <div><dt>{t("Editions")}</dt><dd>{editionCount.toLocaleString()}</dd></div>
          {modelTotal.state === "live" && <div><dt>{t("Models")}</dt><dd>{modelTotal.data.toLocaleString()}</dd></div>}
          {origins.state === "live" && <div><dt>{t("Origins")}</dt><dd>{origins.data.length}</dd></div>}
        </dl>}
      </div>
    </section>

    <div className="page-width discover">
      {savedBooks.length > 0 && <section className="discover__section" aria-labelledby="discover-saved">
        <SectionHeading id="discover-saved" title={t("From your collection")} action={t("Open collection")} href="/saved" count={saved.length} />
        <div className="book-grid book-grid--row">{savedBooks.map(book => <BookCard key={book.id} book={book} />)}</div>
      </section>}

      <section className="discover__section" aria-labelledby="discover-new">
        <SectionHeading id="discover-new" title={t("New releases")} action={t("Browse all")} href="/books" />
        {books.state === "loading" ? <BookGridSkeleton count={8} /> : books.state !== "live" ? <LoadState state={books.state} retry={books.retry} errorMessage="The catalog couldn’t be reached." /> :
          <div className="book-grid book-grid--row">{newest.map((book, index) => <BookCard key={book.id} book={book} loading={index < 4 ? "eager" : "lazy"} />)}</div>}
      </section>

      {origins.state === "live" && origins.data.length > 0 && <section className="discover__section" aria-labelledby="discover-origins">
        <SectionHeading id="discover-origins" title={t("Browse by origin")} />
        <div className="origin-grid">{origins.data.map(origin => <a key={origin.code} className="origin-tile" href={`/books?origin=${encodeURIComponent(origin.code)}`}>
          <span className="origin-tile__code" aria-hidden="true">{origin.code}</span>
          <strong>{t(origin.name)}</strong>
          {origin.count !== undefined && <span>{origin.count} {t(origin.count === 1 ? "publication" : "publications")}</span>}
        </a>)}</div>
      </section>}

      {featuredModels.length > 0 && <section className="discover__section" aria-labelledby="discover-models">
        <SectionHeading id="discover-models" title={t("Featured models")} action={t("All models")} href="/models" />
        <div className="person-grid person-grid--row">{featuredModels.map(model => <a key={model.id} className="person-card" href={`/models/${encodeURIComponent(model.id)}`}>
          <span className="person-card__portrait">{showCatalogImages && model.coverUrl ? <img src={model.coverUrl} alt="" loading="lazy" /> : <span aria-hidden="true">{model.name.slice(0, 1)}</span>}</span>
          <strong>{model.name}</strong>
          {model.alias && <small>{model.alias}</small>}
          <span>{model.workCount} {t(model.workCount === 1 ? "photobook" : "photobooks")}</span>
        </a>)}</div>
      </section>}

      <section className="discover__section market-pulse" aria-label={t("Market pulse")}>
        <MarketList status="active" title="Latest offers" href="/active" />
        <MarketList status="sold" title="Recently sold" href="/sold" />
      </section>

      <section className="discover__section explainer" aria-labelledby="discover-how">
        <SectionHeading id="discover-how" title={t("How the catalog is organised")} action={t("Read the methodology")} href="/about" />
        <ol className="explainer__steps">
          <li><span className="eyebrow">01</span><h3>{t("Work")}</h3><p>{t("The photobook or magazine issue itself — its title, featured people, photographer and origin.")}</p></li>
          <li><span className="eyebrow">02</span><h3>{t("Edition")}</h3><p>{t("Each physical or digital release, with its own ISBN, publisher, release date and format.")}</p></li>
          <li><span className="eyebrow">03</span><h3>{t("Listing")}</h3><p>{t("Retail and marketplace records for an edition, kept with their source, condition and observation date.")}</p></li>
        </ol>
      </section>
    </div>
  </>;
}
