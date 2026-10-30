import { useEffect, useState } from "react";
import Icon from "./Icon";
import { LoadState, Pagination } from "./Page";
import { usePreferences } from "../lib/preferences";
import { setSearchParams } from "../lib/router";
import { loadSources, useLoader, useResource } from "../lib/catalog";

/** Retail and marketplace listings (active or sold) with shared filters. */
export default function ListingsView({ status, scope = {}, syncUrl = false }) {
  const { t, formatPrice } = usePreferences();
  const initial = new URLSearchParams(syncUrl ? window.location.search : "");
  const [filters, setFilters] = useState(() => ({ q: initial.get("q") || "", publicationType: initial.get("publicationType") || "", format: status === "sold" ? "physical" : initial.get("format") || "", source: initial.get("source") || "" }));
  const [query, setQuery] = useState(filters.q);
  const [page, setPage] = useState(Number(initial.get("page")) || 1);
  const sources = useLoader(loadSources, []);
  useEffect(() => {
    if (syncUrl) setSearchParams({ ...filters, format: status === "sold" ? "" : filters.format, model: scope.model, publisher: scope.publisher, name: scope.name, page: page > 1 ? String(page) : "" });
  }, [filters, page, syncUrl, status, scope.model, scope.publisher, scope.name]);
  const params = new URLSearchParams({ q: filters.q, status, page: String(page), pageSize: "24" });
  for (const [key, value] of Object.entries({ format: filters.format, publicationType: filters.publicationType, source: filters.source, model: scope.model, publisher: scope.publisher })) if (value) params.set(key, value);
  const result = useResource(`/v1/listings?${params}`);
  const update = (key, value) => { setFilters(current => ({ ...current, [key]: value })); setPage(1); };
  const sold = status === "sold";
  return <div className="listings-view">
    <div className={`toolbar toolbar--wrap listing-toolbar${sold ? " listing-toolbar--compact" : ""}`}>
      <form className="search-field" role="search" onSubmit={event => { event.preventDefault(); update("q", query.trim()); }}>
        <Icon name="search" size={18} />
        <input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder={t("Title, person, or publisher")} aria-label={t("Search listings")} />
        <button type="submit" className="button">{t("Search")}</button>
      </form>
      <label className="select-field"><span>{t("Type")}</span><select value={filters.publicationType} onChange={event => update("publicationType", event.target.value)}><option value="">{t("All publication types")}</option><option value="photobook">{t("Photobooks")}</option><option value="magazine_issue">{t("Magazine issues")}</option></select></label>
      {!sold && <label className="select-field"><span>{t("Format")}</span><select value={filters.format} onChange={event => update("format", event.target.value)}><option value="">{t("All formats")}</option><option value="physical">{t("Physical")}</option><option value="digital">{t("Digital")}</option></select></label>}
      <label className="select-field"><span>{t("Source")}</span><select value={filters.source} onChange={event => update("source", event.target.value)}><option value="">{t("All sources")}</option>{(sources.data || []).map(source => <option key={source.id} value={source.id}>{source.name}</option>)}</select></label>
    </div>
    {result.state === "live" && <p className="results-count" role="status">{result.data.total.toLocaleString()} {t(result.data.total === 1 ? "listing" : "listings")}</p>}
    <LoadState state={result.state} retry={result.retry} empty={result.state === "live" && !result.data.items.length} />
    {result.state === "live" && result.data.items.length > 0 && <>
      <div className="ledger-wrap" role="region" aria-label={t(sold ? "Sold listings" : "Active listings")} tabIndex={0}>
        <table className="ledger">
          <thead><tr><th>{t("Publication / edition")}</th><th>{t("Source")}</th><th className="ledger__num">{t(sold ? "Sold price" : "Offer price")}</th><th>{t("Condition")}</th><th>{t("Observed")}</th><th><span className="visually-hidden">{t("Links")}</span></th></tr></thead>
          <tbody>{result.data.items.map(item => <tr key={item.id}>
            <td className="ledger__title"><a href={`/books/${encodeURIComponent(item.workSlug)}`}><strong>{item.workTitle}</strong></a><small>{[item.featuredNames?.join(" · "), item.editionLabel, item.format, item.publisher].filter(Boolean).join(" · ")}</small></td>
            <td data-label={t("Source")}>{item.source?.name}<small>{item.source?.region}</small></td>
            <td data-label={t(sold ? "Sold price" : "Offer price")} className="ledger__num"><strong>{formatPrice(item.priceMinor, item.currency)}</strong><small>{t(sold ? "Completed sale" : item.priceType === "auction_current" ? "Current bid" : item.priceCategory?.includes("retail") ? "Retail asking price" : "Asking price")}</small></td>
            <td data-label={t("Condition")}>{item.condition || t("Not recorded")}{item.shippingText && <small>{item.shippingText}</small>}</td>
            <td data-label={t("Observed")}>{item.observedAt ? <time dateTime={item.observedAt}>{new Date(item.observedAt).toLocaleDateString()}</time> : t("Not recorded")}</td>
            <td className="ledger__links">{item.url && <a className="text-link" href={item.url} target="_blank" rel="noreferrer" data-external-link>{t("View source")} ↗</a>}</td>
          </tr>)}</tbody>
        </table>
      </div>
      <Pagination page={page} pages={result.data.totalPages} onPage={setPage} />
    </>}
  </div>;
}
