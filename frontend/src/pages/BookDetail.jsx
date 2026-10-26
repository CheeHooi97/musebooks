import { useEffect, useMemo, useState } from "react";
import SeoHead from "../components/SeoHead";
import Icon from "../components/Icon";
import EditionPrices from "../components/EditionPrices";
import BookCard, { BookCover } from "../components/BookCard";
import { Breadcrumb, LoadState, SectionHeading } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { useCollection } from "../lib/collection";
import { isMobileApp, showCatalogImages } from "../lib/platform";
import { publicationDate } from "../lib/seo";
import { bookAnswers, bookFactSummary } from "../lib/book-answers";
import { priceLabel, primaryListing } from "../lib/price-policy";
import { bookPeople, bookTitle, editionFormatLabel, getBook, isMagazine, publicationTypeLabel, useResource } from "../lib/catalog";

function bootstrapBook(slug) {
  try { const book = JSON.parse(document.getElementById("musebooks-bootstrap")?.textContent || "{}").book; return book?.slug === slug ? book : undefined; }
  catch { return undefined; }
}

function RelatedBooks({ title, path, href, currentId, id }) {
  const { t } = usePreferences();
  const related = useResource(path);
  const items = related.state === "live" ? related.data.items.filter(book => book.id !== currentId).slice(0, 4) : [];
  if (!items.length) return null;
  return <section className="detail-section" aria-labelledby={id}>
    <SectionHeading id={id} title={title} action={t("View all")} href={href} />
    <div className="book-grid book-grid--row">{items.map(book => <BookCard key={book.id} book={book} />)}</div>
  </section>;
}

function useShare(book) {
  const [state, setState] = useState("idle");
  const share = async () => {
    const siteOrigin = isMobileApp ? import.meta.env.VITE_SITE_URL || "https://musebooks.my" : window.location.origin;
    const url = new URL(`/books/${encodeURIComponent(book.slug)}`, siteOrigin).toString();
    try {
      if (isMobileApp) { const { Share } = await import("@capacitor/share"); await Share.share({ title: bookTitle(book), text: book.originalTitle, url, dialogTitle: `Share this ${publicationTypeLabel(book).toLowerCase()}` }); setState("shared"); }
      else if (navigator.share) { await navigator.share({ title: bookTitle(book), url }); setState("shared"); }
      else if (navigator.clipboard?.writeText) { await navigator.clipboard.writeText(url); setState("copied"); }
      else return;
      window.setTimeout(() => setState("idle"), 1800);
    } catch (error) { if (!(error instanceof Error && error.name === "AbortError")) setState("idle"); }
  };
  return [state, share];
}

function Detail({ book, editionId, setEditionId }) {
  const { t, formatPrice } = usePreferences();
  const { isSaved, toggleSaved } = useCollection();
  const [shareState, share] = useShare(book);
  // Without an explicit choice, lead with the first edition that has a recorded price.
  const edition = book.editions.find(item => item.id === editionId) || book.editions.find(item => primaryListing(item)) || book.editions[0];
  const listing = primaryListing(edition, "");
  const people = bookPeople(book);
  const saved = isSaved(book.id);
  const firstModel = (book.models || book.coverModels || []).find(model => model.id);
  const publisher = book.editions.map(item => item.publisherProfile).find(profile => profile?.id);
  const gallery = useMemo(() => Array.from(new Map([
    ...(edition.gallery || []).map(asset => ({ ...asset, attribution: "Publisher" })),
    ...(edition.listings || []).flatMap(item => (item.gallery || []).map(asset => ({ ...asset, attribution: item.source?.name || "Listing source" }))),
  ].map(asset => [asset.storageUrl, asset])).values()), [edition]);
  const specs = [
    ["Publication type", t(publicationTypeLabel(book))],
    edition.seriesName && ["Series", edition.seriesName],
    isMagazine(book) && ["Issue month", book.issueMonth || t("Not recorded")],
    isMagazine(book) && book.issueNumber && ["Issue number", book.issueNumber],
    ["Photographer", book.photographer || t("Not recorded")],
    ["Origin", t(book.origin.name)],
    ["Format", t(editionFormatLabel(edition, book))],
    ["Language", edition.language || t("Not recorded")],
    ["Pages", edition.pageCount ? `${edition.pageCount} ${t("pages")}` : t("Not recorded")],
    [edition.format === "digital" ? "Store release" : "Published", publicationDate(edition) || t("Not recorded")],
    ["ISBN", edition.isbn || t("Not recorded")],
    ["Dimensions", edition.dimensions || t("Not recorded")],
    ["Publisher", edition.publisherProfile?.id ? <a href={`/publishers/${encodeURIComponent(edition.publisherProfile.id)}`}>{edition.publisherProfile.name}</a> : edition.publisher || t("Not recorded")],
    ["Market", edition.editionMarket || t("Not recorded")],
  ].filter(Boolean);
  return <article className="book-detail" aria-labelledby="book-title">
    <Breadcrumb items={[[t("Browse"), "/books"], [book.originalTitle]]} />
    <section className="book-hero">
      {showCatalogImages && <div className="book-hero__media">
        <BookCover book={book} edition={edition} loading="eager" />
        {book.editions.length > 1 && <div className="edition-thumbs" role="group" aria-label={t("Editions")}>
          {book.editions.map(item => <button key={item.id} type="button" className={item.id === edition.id ? "is-active" : ""} onClick={() => setEditionId(item.id)} aria-pressed={item.id === edition.id} aria-label={`${t("View")} ${item.editionLabel}`}><BookCover book={book} edition={item} compact /></button>)}
        </div>}
      </div>}
      <div className="book-hero__info">
        <p className="eyebrow">{t(publicationTypeLabel(book))} · {t(book.origin.name)}{publicationDate(edition) ? ` · ${publicationDate(edition).slice(0, 4)}` : ""}</p>
        <h1 id="book-title" tabIndex={-1}>{book.originalTitle}</h1>
        {book.englishTitle && <p className="book-hero__subtitle">{book.englishTitle}</p>}
        {people.length > 0 && <div className="person-chips" aria-label={t(isMagazine(book) ? "Cover models" : "Models & featured people")}>
          {people.map(person => person.id ? <a key={person.id} className="chip" href={`/models/${encodeURIComponent(person.id)}`}><Icon name="person" size={14} />{person.name}</a> : <span key={person.name} className="chip">{person.name}</span>)}
        </div>}
        {book.summary && <p className="book-hero__summary">{book.summary}</p>}
        <div className="price-panel">
          <div>
            <span className="eyebrow">{edition.editionLabel}</span>
            <strong>{listing ? formatPrice(listing.priceMinor, listing.currency) : t("No price recorded")}</strong>
            <span>{t(priceLabel(edition, listing))}{listing?.source?.name ? ` · ${listing.source.name}` : ""}</span>
          </div>
          <div className="price-panel__actions">
            {listing?.url && <a className="button" href={listing.url} target="_blank" rel="noreferrer" data-external-link><Icon name="external" size={16} />{t("Visit source site")}</a>}
            <button type="button" className={`button button--ghost${saved ? " is-saved" : ""}`} onClick={() => toggleSaved(book.id)} aria-pressed={saved}><Icon name="bookmark" size={16} />{saved ? t("Saved") : t("Save")}</button>
            <button type="button" className="button button--ghost" onClick={share}><Icon name="share" size={16} />{shareState === "shared" ? t("Share sheet opened") : shareState === "copied" ? t("Link copied") : t("Share")}</button>
          </div>
        </div>
        <dl className="key-facts">
          {specs.slice(0, 6).map(([label, value]) => <div key={label}><dt>{t(label)}</dt><dd>{value}</dd></div>)}
        </dl>
      </div>
    </section>

    <section className="detail-section" id="available-editions" aria-labelledby="editions-title">
      <SectionHeading id="editions-title" title={t("Editions")} count={book.editions.length} />
      <div className="edition-list" role="list">
        {book.editions.map(item => {
          const itemListing = primaryListing(item);
          const active = item.id === edition.id;
          return <div role="listitem" className={`edition-row${active ? " is-active" : ""}`} key={item.id}>
            <button type="button" className="edition-row__select" onClick={() => setEditionId(item.id)} aria-pressed={active}>
              <strong>{item.editionLabel}</strong>
              <span>{t(editionFormatLabel(item, book))}{publicationDate(item) ? ` · ${publicationDate(item)}` : ""}{item.publisher ? ` · ${item.publisher}` : ""}{item.seriesName ? ` · ${item.seriesName}` : ""}</span>
            </button>
            <span className="edition-row__price">{itemListing ? formatPrice(itemListing.priceMinor, itemListing.currency) : t("No price")}<small>{t(priceLabel(item, itemListing))}</small></span>
          </div>;
        })}
      </div>
    </section>

    <div className="detail-section" id="platform-prices"><EditionPrices edition={edition} publicationType={book.publicationType} /></div>

    <section className="detail-section" aria-labelledby="specs-title">
      <SectionHeading id="specs-title" title={t("Edition details")} />
      <dl className="spec-table">{specs.map(([label, value]) => <div key={label}><dt>{t(label)}</dt><dd>{value}</dd></div>)}</dl>
      {edition.contentSummary && <p className="prose">{edition.contentSummary}</p>}
      {/^https?:\/\//i.test(edition.metadataSourceUrl || "") && <p><a className="text-link" href={edition.metadataSourceUrl} target="_blank" rel="noreferrer" data-external-link>{t("Edition metadata source")} ↗</a></p>}
    </section>

    {showCatalogImages && gallery.length > 0 && <section className="detail-section" aria-labelledby="gallery-title">
      <SectionHeading id="gallery-title" title={t("Product images")} />
      <div className="gallery-grid">{gallery.map(asset => <figure key={asset.storageUrl}>
        <a href={asset.sourceUrl} target="_blank" rel="noreferrer" data-external-link><img src={asset.storageUrl} alt={`${edition.editionLabel} — ${asset.attribution} product image`} loading="lazy" /></a>
        <figcaption><a href={asset.sourceUrl} target="_blank" rel="noreferrer" data-external-link>{asset.attribution}</a></figcaption>
      </figure>)}</div>
    </section>}

    {firstModel && <RelatedBooks id="related-model" title={`${t("More with")} ${firstModel.name}`} path={`/v1/models/${encodeURIComponent(firstModel.id)}/books?pageSize=5`} href={`/models/${encodeURIComponent(firstModel.id)}`} currentId={book.id} />}
    {publisher && <RelatedBooks id="related-publisher" title={`${t("More from")} ${publisher.name}`} path={`/v1/publishers/${encodeURIComponent(publisher.id)}/books?pageSize=5`} href={`/publishers/${encodeURIComponent(publisher.id)}`} currentId={book.id} />}

    <section className="detail-section book-questions" aria-labelledby="book-questions-title">
      <SectionHeading id="book-questions-title" title={t(isMagazine(book) ? "About this magazine issue" : "About this photobook")} />
      <p className="prose">{bookFactSummary(book)}</p>
      <div className="faq">{bookAnswers(book).map(({ question, answer }) => <details key={question}><summary>{question}</summary><p>{answer}</p></details>)}</div>
    </section>
  </article>;
}

export default function BookPage({ slug, search }) {
  const { t } = usePreferences();
  const [result, setResult] = useState(() => { const book = bootstrapBook(slug); return book ? { state: "live", book } : { state: "loading" }; });
  const [attempt, setAttempt] = useState(0);
  const [editionId, setEditionIdState] = useState(() => new URLSearchParams(search).get("edition") || "");
  useEffect(() => {
    let active = true;
    getBook(slug).then(book => { if (active) setResult({ state: "live", book }); })
      .catch(error => { if (active) setResult(current => current.book ? current : { state: error.message === "missing" ? "missing" : "error" }); });
    return () => { active = false; };
  }, [slug, attempt]);
  const setEditionId = id => {
    setEditionIdState(id);
    const params = new URLSearchParams(window.location.search); params.set("edition", id);
    window.history.replaceState(null, "", `${window.location.pathname}?${params}`);
  };
  const book = result.book;
  return <div className="page-width">
    <SeoHead path={`/books/${encodeURIComponent(slug)}`} book={book} pending={result.state === "loading"} noindex={result.state === "missing"} />
    {result.state === "live" && book.editions?.length ? <Detail book={book} editionId={editionId} setEditionId={setEditionId} /> :
      result.state === "live" ? <div className="route-state"><h1>{book.originalTitle}</h1><p>{t("No editions recorded yet.")}</p><a className="button" href="/books">{t("Browse the catalog")}</a></div> :
      result.state === "missing" ? <div className="route-state"><h1>{t("Publication not found.")}</h1><a className="button" href="/books">{t("Browse the catalog")}</a></div> :
      <div className="route-state"><LoadState state={result.state} retry={() => setAttempt(value => value + 1)} loadingMessage="Loading publication…" errorMessage="This publication couldn’t be loaded." /></div>}
  </div>;
}
