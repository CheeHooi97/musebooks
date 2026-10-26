import { useEffect, useState } from "react";
import SeoHead from "../components/SeoHead";
import Icon from "../components/Icon";
import { LoadState, PageHeader, Pagination } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { showCatalogImages } from "../lib/platform";
import { setSearchParams } from "../lib/router";
import { useResource } from "../lib/catalog";

// Models and publishers come from MuseBooks catalog credits only: the API lists
// people and companies attached to at least one published work.
export default function Directory({ kind, search }) {
  const { t } = usePreferences();
  const params = new URLSearchParams(search);
  const q = params.get("q") || "";
  const page = Number(params.get("page")) || 1;
  const [query, setQuery] = useState(q);
  useEffect(() => setQuery(q), [q]);
  const result = useResource(`/v1/${kind}?${new URLSearchParams({ q, page: String(page), pageSize: "48" })}`);
  const models = kind === "models";
  return <div className="page-width">
    <SeoHead path={`/${kind}`} noindex={Boolean(q) || page > 1} />
    <PageHeader eyebrow={t("Catalog credits")} title={t(models ? "Models & featured people" : "Publishers")}
      intro={t(models ? "Every model, idol and entertainer credited on a verified MuseBooks photobook or magazine cover." : "Publishers with at least one verified edition in the catalog.")} />
    <div className="toolbar">
      <form className="search-field" role="search" onSubmit={event => { event.preventDefault(); setSearchParams({ q: query.trim() }); }}>
        <Icon name="search" size={18} />
        <input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder={t("Search by name")} aria-label={t(models ? "Search models" : "Search publishers")} />
        <button type="submit" className="button">{t("Search")}</button>
      </form>
      {result.state === "live" && <p className="results-count" role="status">{result.data.total.toLocaleString()} {t(result.data.total === 1 ? "catalog entry" : "catalog entries")}</p>}
    </div>
    <LoadState state={result.state} retry={result.retry} empty={result.state === "live" && !result.data.items.length} />
    {result.state === "live" && result.data.items.length > 0 && <>
      <div className={models ? "person-grid person-grid--directory" : "publisher-list"}>
        {result.data.items.map(entry => models ?
          <a key={entry.id} className="person-card" href={`/models/${encodeURIComponent(entry.id)}`}>
            {showCatalogImages && <span className="person-card__portrait">{entry.coverUrl ? <img src={entry.coverUrl} alt="" loading="lazy" /> : <span aria-hidden="true">{entry.name.slice(0, 1)}</span>}</span>}
            <strong>{entry.name}</strong>
            {entry.originalName && entry.originalName !== entry.name && <small>{entry.originalName}</small>}
            <span>{entry.workCount} {t(entry.workCount === 1 ? "publication" : "publications")} · {entry.editionCount} {t(entry.editionCount === 1 ? "edition" : "editions")}</span>
          </a> :
          <a key={entry.id} className="publisher-row" href={`/publishers/${encodeURIComponent(entry.id)}`}>
            {showCatalogImages && <span className="publisher-row__thumb">{entry.coverUrl ? <img src={entry.coverUrl} alt="" loading="lazy" /> : <span aria-hidden="true">{entry.name.slice(0, 1)}</span>}</span>}
            <strong>{entry.name}</strong>
            <span>{entry.workCount} {t(entry.workCount === 1 ? "publication" : "publications")}</span>
            <span>{entry.editionCount} {t(entry.editionCount === 1 ? "edition" : "editions")}</span>
            <Icon name="arrow" size={18} />
          </a>)}
      </div>
      <Pagination page={page} pages={result.data.totalPages} onPage={next => { setSearchParams({ q, page: next > 1 ? String(next) : "" }); window.scrollTo(0, 0); }} />
    </>}
  </div>;
}
