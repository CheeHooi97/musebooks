import { useEffect, useState } from "react";
import SeoHead from "../components/SeoHead";
import Icon from "../components/Icon";
import BookCard from "../components/BookCard";
import ListingsView from "../components/ListingsView";
import { Breadcrumb, LoadState, Pagination } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { showCatalogImages } from "../lib/platform";
import { useResource } from "../lib/catalog";
import { profileFactSummary } from "../lib/book-answers";

const EMPTY = { q: "", publicationType: "", format: "", language: "", year: "", model: "" };

function Works({ kind, id }) {
  const { t } = usePreferences();
  const initial = new URLSearchParams(window.location.search);
  const [filters, setFilters] = useState(() => Object.fromEntries(Object.keys(EMPTY).map(key => [key, initial.get(key) || ""])));
  const [page, setPage] = useState(Number(initial.get("page")) || 1);
  const params = new URLSearchParams({ ...filters, page: String(page), pageSize: "24" });
  if (filters.year && !/^[1-9]\d{3}$/.test(filters.year)) params.delete("year");
  const books = useResource(`/v1/${kind}/${id}/books?${params}`);
  useEffect(() => {
    const search = new URLSearchParams({ ...filters, page: page > 1 ? String(page) : "" });
    for (const [key, value] of [...search]) if (!value) search.delete(key);
    window.history.replaceState(null, "", `${window.location.pathname}${search.size ? `?${search}` : ""}`);
  }, [filters, page]);
  const update = (key, value) => { setFilters(current => ({ ...current, [key]: value })); setPage(1); };
  const filtered = Object.values(filters).some(Boolean);
  return <>
    <form className="toolbar toolbar--wrap" onSubmit={event => event.preventDefault()}>
      <label className="search-field"><Icon name="search" size={18} /><input type="search" value={filters.q} onChange={event => update("q", event.target.value)} placeholder={t("Title or featured person")} aria-label={t("Search catalog records")} /></label>
      <label className="select-field"><span>{t("Type")}</span><select value={filters.publicationType} onChange={event => update("publicationType", event.target.value)}><option value="">{t("All publication types")}</option><option value="photobook">{t("Photobooks")}</option><option value="magazine_issue">{t("Magazine issues")}</option></select></label>
      <label className="select-field"><span>{t("Format")}</span><select value={filters.format} onChange={event => update("format", event.target.value)}><option value="">{t("All formats")}</option><option value="physical">{t("Physical")}</option><option value="digital">{t("Digital")}</option></select></label>
      <label className="select-field select-field--narrow"><span>{t("Year")}</span><input type="number" min="1000" max="9999" value={filters.year} onChange={event => update("year", event.target.value)} placeholder={t("Any")} /></label>
      <label className="select-field select-field--narrow"><span>{t("Language")}</span><input value={filters.language} onChange={event => update("language", event.target.value)} placeholder={t("Any")} /></label>
      {kind === "publishers" && <label className="select-field"><span>{t("Model")}</span><input value={filters.model} onChange={event => update("model", event.target.value)} placeholder={t("Featured model name")} /></label>}
      {filtered && <button type="button" className="text-link" onClick={() => { setFilters(EMPTY); setPage(1); }}>{t("Clear filters")}</button>}
    </form>
    {books.state === "live" && <p className="results-count" role="status">{books.data.total} {t(books.data.total === 1 ? "publication" : "publications")}</p>}
    <LoadState state={books.state} retry={books.retry} empty={books.state === "live" && !books.data.items.length} loadingMessage="Loading photobooks…" />
    {books.state === "live" && books.data.items.length > 0 && <>
      <div className="book-grid">{books.data.items.map(book => <BookCard key={book.id} book={book} showPrice={false} />)}</div>
      <Pagination page={page} pages={books.data.totalPages} onPage={next => { setPage(next); window.scrollTo(0, 0); }} />
    </>}
  </>;
}

export default function DirectoryProfile({ kind, id }) {
  const { t } = usePreferences();
  const [tab, setTab] = useState(() => ["active", "sold"].includes(new URLSearchParams(window.location.search).get("tab")) ? new URLSearchParams(window.location.search).get("tab") : "works");
  const profile = useResource(`/v1/${kind}/${id}`);
  const preview = useResource(`/v1/${kind}/${id}/books?pageSize=24`);
  const entry = profile.data;
  const models = kind === "models";
  const aliases = entry ? [entry.originalName, entry.englishName].filter((name, index, names) => name && name !== entry.name && names.indexOf(name) === index) : [];
  const scope = { [models ? "model" : "publisher"]: id, name: entry?.name };
  return <div className="page-width">
    <SeoHead path={`/${kind}/${id}`} profile={entry ? { ...entry, books: preview.data?.items || [] } : undefined} pending={profile.state === "loading" || profile.state === "error"} noindex={profile.state === "missing" || window.location.search.length > 1} />
    <Breadcrumb items={[[t(models ? "Models" : "Publishers"), `/${kind}`], [entry?.name || "…"]]} />
    {profile.state !== "live" ? <LoadState state={profile.state} retry={profile.retry} /> : <>
      <header className="profile-header">
        {showCatalogImages && <div className="profile-header__portrait">{entry.coverUrl ? <img src={entry.coverUrl} alt="" /> : <span aria-hidden="true">{entry.name.slice(0, 1)}</span>}</div>}
        <div>
          <p className="eyebrow">{t(models ? "Model" : "Publisher")}</p>
          <h1 id="page-title" tabIndex={-1}>{entry.name}</h1>
          {aliases.length > 0 && <p className="profile-header__aliases">{aliases.join(" · ")}</p>}
          <dl className="profile-header__stats">
            <div><dt>{t("Publications")}</dt><dd>{entry.workCount}</dd></div>
            <div><dt>{t("Editions")}</dt><dd>{entry.editionCount}</dd></div>
          </dl>
          <p className="prose">{profileFactSummary(entry, kind, preview.data?.items || [])}</p>
          {entry.officialUrl && <a className="text-link" href={entry.officialUrl} target="_blank" rel="noreferrer" data-external-link>{t(models ? "Profile source" : "Official source")} ↗</a>}
        </div>
      </header>
      <div className="tabs" role="tablist" aria-label={t("Catalog sections")}>
        {[["works", "Publications"], ["active", "For sale"], ["sold", "Sold"]].map(([key, label]) => <button key={key} type="button" role="tab" id={`tab-${key}`} aria-selected={tab === key} aria-controls="profile-panel" className={tab === key ? "is-active" : ""} onClick={() => setTab(key)}>{t(label)}</button>)}
      </div>
      <section id="profile-panel" role="tabpanel" aria-labelledby={`tab-${tab}`}>
        {tab === "works" ? <Works kind={kind} id={id} /> : <ListingsView key={tab} status={tab} scope={scope} />}
      </section>
    </>}
  </div>;
}
