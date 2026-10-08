import { useEffect, useState } from "react";
import { apiUrl } from "../lib/api";
import { usePreferences } from "../lib/preferences";
import SeoHead from "../components/SeoHead";

function useResource(path) {
  const [result, setResult] = useState({ state: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setResult({ state: "loading" });
    fetch(apiUrl(path), { signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error(response.status === 404 ? "missing" : "error");
      return response.json();
    }).then(data => { if (!controller.signal.aborted) setResult({ state: "live", data }); })
      .catch(error => { if (!controller.signal.aborted) setResult({ state: error.message === "missing" ? "missing" : "error" }); });
    return () => controller.abort();
  }, [path, attempt]);
  return { ...result, retry: () => setAttempt(value => value + 1) };
}

export default function DirectoryProfile({ kind, id }) {
  const { t } = usePreferences();
  const initial = new URLSearchParams(window.location.search);
  const [filters, setFilters] = useState(() => ({ q: initial.get("q") || "", format: initial.get("format") || "", language: initial.get("language") || "", year: initial.get("year") || "", model: initial.get("model") || "" }));
  const [page, setPage] = useState(Number(initial.get("page")) || 1);
  const profile = useResource(`/v1/${kind}/${id}`);
  const params = new URLSearchParams({ ...filters, page: String(page), pageSize: "24" });
  if (filters.year && !/^[1-9]\d{3}$/.test(filters.year)) params.delete("year");
  const books = useResource(`/v1/${kind}/${id}/books?${params}`);
  const models = useResource("/v1/models?pageSize=50");
  useEffect(() => { const search = new URLSearchParams({ ...filters, page: String(page) }); for (const [key, value] of [...search]) if (!value) search.delete(key); window.history.replaceState(null, "", `${window.location.pathname}?${search}`); }, [filters, page]);
  const update = (key, value) => { setFilters(current => ({ ...current, [key]: value })); setPage(1); };
  const entry = profile.data;
  const error = resource => <div className="profile-state" role="alert"><p>{t(resource.state === "missing" ? "Catalog profile not found." : "These catalog records could not be loaded.")}</p>{resource.state !== "missing" && <button onClick={resource.retry}>{t("Retry connection")}</button>}</div>;
  return <div className="directory-profile">
    <nav className="book-breadcrumb" aria-label={t("Breadcrumb")}><a href="/">{t("Home")}</a><span>/</span><a href={`/${kind}`}>{t(kind === "models" ? "Models" : "Publishers")}</a>{entry && <><span>/</span><span>{entry.name}</span></>}</nav>
    {profile.state === "loading" ? <p role="status">{t("Loading catalog records…")}</p> : profile.state !== "live" ? error(profile) : <>
      <SeoHead path={`/${kind}/${id}`} profile={entry} noindex={Object.values(filters).some(Boolean)} />
      <header className="profile-heading"><div><h1 id="browser-title">{entry.name}</h1>{[entry.originalName, entry.englishName].filter((name, index, names) => name && name !== entry.name && names.indexOf(name) === index).map(name => <p key={name} className="profile-alias">{name}</p>)}<p>{entry.workCount} {t(entry.workCount === 1 ? "photobook" : "photobooks")} · {entry.editionCount} {t(entry.editionCount === 1 ? "edition" : "editions")}</p>{entry.officialUrl && <a href={entry.officialUrl} target="_blank" rel="noreferrer" data-external-link>{t(kind === "publishers" ? "Official source" : "Profile source")}</a>}</div>{entry.coverUrl && <img src={entry.coverUrl} alt="" />}</header>
      <nav className="profile-navigation" aria-label={t("Catalog sections")}><a href="#profile-books">{t("Photobooks")}</a><a href={`/active?${kind === "models" ? "model" : "publisher"}=${id}&name=${encodeURIComponent(entry.name)}`}>{t("Active listings")}</a><a href={`/sold?${kind === "models" ? "model" : "publisher"}=${id}&name=${encodeURIComponent(entry.name)}`}>{t("Sold listings")}</a></nav>
      <section id="profile-books"><h2>{t("Photobooks")}</h2><form className="browser-filters profile-filters" onSubmit={event => event.preventDefault()}>
        <label>{t("Search photobooks")}<input type="search" value={filters.q} onChange={event => update("q", event.target.value)} placeholder={t("Title or featured person")} /></label>
        <label>{t("Format")}<select value={filters.format} onChange={event => update("format", event.target.value)}><option value="">{t("All formats")}</option><option value="physical">{t("Physical")}</option><option value="digital">{t("Digital")}</option></select></label>
        <label>{t("Language")}<input value={filters.language} onChange={event => update("language", event.target.value)} placeholder={t("Any language")} /></label>
        <label>{t("Release year")}<input type="number" min="1000" max="9999" value={filters.year} onChange={event => update("year", event.target.value)} placeholder={t("Any year")} /></label>
        {kind === "publishers" && <label>{t("Model")}<input list="profile-models" value={filters.model} onChange={event => update("model", event.target.value)} placeholder={t("Featured model name")} /><datalist id="profile-models">{models.data?.items?.map(model => <option key={model.id} value={model.name}>{model.name}</option>)}</datalist></label>}
        {Object.values(filters).some(Boolean) && <button type="button" onClick={() => {setFilters({q:"",format:"",language:"",year:"",model:""});setPage(1);}}>{t("Clear filters")}</button>}
      </form>
      {books.state === "loading" ? <p className="profile-state" role="status">{t("Loading photobooks…")}</p> : books.state !== "live" ? error(books) : <>
        <p className="browser-count" role="status">{books.data.total} {t(books.data.total === 1 ? "photobook" : "photobooks")}</p>
        {!books.data.items.length && <p className="profile-state">{t("No verified records match these filters.")}</p>}
        <div className="profile-book-grid">{books.data.items.map(book => <article className="profile-book" key={book.id}>
          <a href={`/books/${encodeURIComponent(book.slug)}`} className="profile-book-cover">{book.coverUrl ? <img src={book.coverUrl} alt="" loading="lazy" /> : <span>{t("Cover unavailable")}</span>}</a>
          <div><h3><a href={`/books/${encodeURIComponent(book.slug)}`}>{book.originalTitle}</a></h3><p className="profile-book-models">{book.models?.map((model, index) => <span key={model.id}>{index > 0 && " · "}<a href={`/models/${encodeURIComponent(model.id)}`}>{model.name}</a></span>)}</p><ul className="profile-editions">{book.editions.map(edition => <li key={edition.id}><span>{t(edition.format === "digital" ? "Digital" : "Physical")}</span> {edition.editionLabel}{edition.releaseDate && <small> · {new Date(edition.releaseDate).getFullYear()}</small>}</li>)}</ul><a className="profile-book-link" href={`/books/${encodeURIComponent(book.slug)}#platform-prices-title`}>{t("Compare platform prices")}</a></div>
        </article>)}</div>
        {books.data.totalPages > 1 && <nav className="catalog-pagination" aria-label={t("Results pages")}><button disabled={page <= 1} onClick={() => setPage(page - 1)}>{t("Previous")}</button><span>{t("Page")} {page} {t("of")} {books.data.totalPages}</span><button disabled={page >= books.data.totalPages} onClick={() => setPage(page + 1)}>{t("Next")}</button></nav>}
      </>}
      </section>
    </>}
  </div>;
}
