import { useEffect, useState } from "react";
import SeoHead from "../components/SeoHead";
import Icon from "../components/Icon";
import BookCard, { BookGridSkeleton } from "../components/BookCard";
import { LoadState, PageHeader, Pagination } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { hasSearchFilters } from "../lib/seo";
import { pushBackHandler, setSearchParams } from "../lib/router";
import { loadOrigins, useLoader, useResource } from "../lib/catalog";

const PAGE_SIZE = 48;
const FILTER_KEYS = ["q", "origin", "publicationType", "format", "availability", "sort"];

function readFilters(search) {
  const params = new URLSearchParams(search);
  return Object.fromEntries(FILTER_KEYS.map(key => [key, params.get(key) || ""]));
}

function Choice({ name, value, current, label, onChange, disabled }) {
  return <label className="choice">
    <input type="radio" name={name} checked={current === value} disabled={disabled} onChange={() => onChange(value)} onClick={() => current === value && onChange("")} />
    <span>{label}</span>
  </label>;
}

export default function Browse({ search }) {
  const { t } = usePreferences();
  const filters = readFilters(search);
  const [query, setQuery] = useState(filters.q);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [page, setPage] = useState(1);
  const params = new URLSearchParams({ page: String(page), pageSize: String(PAGE_SIZE), sort: filters.sort || "newest" });
  for (const key of ["q", "origin", "publicationType", "format", "availability"]) if (filters[key]) params.set(key, filters[key].trim());
  const books = useResource(`/v1/books?${params}`);
  const origins = useLoader(loadOrigins, []);
  const update = (key, value) => {
    const next = { ...filters, [key]: value };
    if (key === "format" && value === "digital" && next.availability === "completed") next.availability = "";
    setSearchParams(next);
    setPage(1);
  };
  useEffect(() => { setQuery(filters.q); }, [filters.q]);
  useEffect(() => {
    if (!sheetOpen) return undefined;
    const release = pushBackHandler(() => setSheetOpen(false));
    const escape = event => { if (event.key === "Escape") setSheetOpen(false); };
    document.addEventListener("keydown", escape);
    document.body.classList.add("has-sheet");
    return () => { release(); document.removeEventListener("keydown", escape); document.body.classList.remove("has-sheet"); };
  }, [sheetOpen]);
  const results = books.state === "live" ? books.data.items : [];
  const total = books.state === "live" ? books.data.total : 0;
  const pages = books.state === "live" ? books.data.totalPages : 0;
  const originName = code => origins.data?.find(origin => origin.code === code)?.name || code;
  const chips = [
    filters.q && ["q", `“${filters.q}”`],
    filters.origin && ["origin", t(originName(filters.origin))],
    filters.publicationType && ["publicationType", t(filters.publicationType === "magazine_issue" ? "Magazine issues" : "Photobooks")],
    filters.format && ["format", t(filters.format === "digital" ? "Digital edition" : "Physical")],
    filters.availability && ["availability", t(filters.availability === "active" ? "In stock" : filters.availability === "completed" ? "Sold (physical)" : "Availability unknown")],
  ].filter(Boolean);
  const activeCount = chips.filter(([key]) => key !== "q").length;
  const panel = <div className="filter-panel__groups">
    <fieldset><legend>{t("Origin")}</legend>
      {origins.state === "live" ? origins.data.map(origin => <Choice key={origin.code} name="origin" value={origin.code} current={filters.origin} onChange={value => update("origin", value)} label={<>{t(origin.name)}{origin.count !== undefined && <em>{origin.count}</em>}</>} />) : <p className="load-state">{t("Loading…")}</p>}
    </fieldset>
    <fieldset><legend>{t("Publication type")}</legend>
      <Choice name="type" value="photobook" current={filters.publicationType} onChange={value => update("publicationType", value)} label={t("Photobooks")} />
      <Choice name="type" value="magazine_issue" current={filters.publicationType} onChange={value => update("publicationType", value)} label={t("Magazine issues")} />
    </fieldset>
    <fieldset><legend>{t("Format")}</legend>
      <Choice name="format" value="physical" current={filters.format} onChange={value => update("format", value)} label={t("Physical")} />
      <Choice name="format" value="digital" current={filters.format} onChange={value => update("format", value)} label={t("Digital edition")} />
    </fieldset>
    <fieldset><legend>{t("Availability")}</legend>
      <Choice name="availability" value="active" current={filters.availability} onChange={value => update("availability", value)} label={t("In stock")} />
      <Choice name="availability" value="unknown" current={filters.availability} onChange={value => update("availability", value)} label={t("Availability unknown")} />
      <Choice name="availability" value="completed" current={filters.availability} disabled={filters.format === "digital"} onChange={value => update("availability", value)} label={t("Sold (physical)")} />
    </fieldset>
  </div>;
  return <>
    <SeoHead path="/books" noindex={hasSearchFilters(search)} />
    <div className="page-width">
      <PageHeader eyebrow={t("Catalog")} title={t("Browse publications")} intro={t("Every verified photobook and magazine issue. Filter by origin, format and availability; each card shows the best recorded price for its edition.")} />
      <div className="toolbar">
        <form className="search-field" role="search" action="/books" toolname="search_catalog" tooldescription="Search the MuseBooks catalog of photobooks and magazine issues by title, model, or publisher. Read-only." onSubmit={event => { event.preventDefault(); update("q", query.trim()); }}>
          <Icon name="search" size={18} />
          <input type="search" name="q" toolparamdescription="Title, model, photographer, or publisher name" value={query} onChange={event => setQuery(event.target.value)} placeholder={t("Title, model, photographer or publisher")} aria-label={t("Search publications")} />
          <button type="submit" className="button">{t("Search")}</button>
        </form>
        <button type="button" className="button button--ghost filter-toggle" aria-expanded={sheetOpen} aria-controls="filter-panel" onClick={() => setSheetOpen(true)}>
          <Icon name="filter" size={18} />{t("Filters")}{activeCount > 0 && <span className="badge">{activeCount}</span>}
        </button>
        <label className="select-field"><span>{t("Sort by")}</span>
          <select value={filters.sort || "newest"} onChange={event => update("sort", event.target.value === "newest" ? "" : event.target.value)}>
            <option value="newest">{t("Newest release")}</option><option value="oldest">{t("Oldest release")}</option><option value="title">{t("Title")}</option>
          </select>
        </label>
      </div>
      <div className="browse-layout">
        <aside id="filter-panel" className={`filter-panel${sheetOpen ? " is-open" : ""}`} aria-label={t("Catalog filters")}>
          <div className="filter-panel__head">
            <h2>{t("Filters")}</h2>
            {activeCount > 0 && <button type="button" className="text-link" onClick={() => { setSearchParams({ q: filters.q, sort: filters.sort }); setPage(1); }}>{t("Clear all")}</button>}
            <button type="button" className="icon-button filter-panel__close" onClick={() => setSheetOpen(false)} aria-label={t("Close filters")}><Icon name="close" size={20} /></button>
          </div>
          {panel}
          <div className="filter-panel__foot"><button type="button" className="button button--block" onClick={() => setSheetOpen(false)}>{t("Show")} {total} {t(total === 1 ? "publication" : "publications")}</button></div>
        </aside>
        {sheetOpen && <div className="sheet-backdrop" onClick={() => setSheetOpen(false)} aria-hidden="true" />}
        <section className="browse-results" aria-label={t("Catalog results")}>
          <div className="results-bar">
            <p className="results-count" role="status">{books.state === "loading" ? t("Loading catalog") : `${total.toLocaleString()} ${t(total === 1 ? "publication" : "publications")}`}</p>
            {chips.length > 0 && <ul className="chips">{chips.map(([key, label]) => <li key={key}><button type="button" className="chip" onClick={() => update(key, "")} aria-label={`${t("Remove filter")}: ${label}`}>{label}<Icon name="close" size={14} /></button></li>)}</ul>}
          </div>
          {books.state === "loading" ? <BookGridSkeleton count={12} /> : books.state !== "live" ? <LoadState state={books.state} retry={books.retry} errorMessage="The catalog couldn’t be reached." /> : results.length === 0 ?
            <div className="empty-state"><Icon name="search" size={26} /><h2>{t("No titles match those filters.")}</h2><p>{t("Try clearing a filter or searching a wider title, artist, or place.")}</p><button type="button" className="button button--ghost" onClick={() => { setSearchParams({}); setPage(1); }}>{t("Clear filters")}</button></div> :
            <>
              <div className="book-grid">{results.map((book, index) => <BookCard key={book.id} book={book} filters={{ format: filters.format, availability: filters.availability }} loading={index < 4 ? "eager" : "lazy"} />)}</div>
              <Pagination page={page} pages={pages} onPage={next => { setPage(next); window.scrollTo(0, 0); }} />
            </>}
        </section>
      </div>
    </div>
  </>;
}
