import { useEffect, useMemo, useState } from "react";
import Icon from "./Icon";
import EditionPrices from "./EditionPrices";
import { LoadState, Pagination } from "./Page";
import { apiUrl } from "../lib/api";
import { usePreferences } from "../lib/preferences";
import { showCatalogImages } from "../lib/platform";
import { aliasIndex, marketplaceGroups } from "../lib/marketplace-groups";
import { formatPrice } from "../lib/price-policy";
import { useLoader, useResource } from "../lib/catalog";

const PAGE_SIZE = 24;

async function loadJapanOffers() {
  const load = async page => {
    const response = await fetch(apiUrl(`/v1/marketplace-listings?region=JP&scope=offers&status=all&pageSize=50&page=${page}`));
    if (!response.ok) throw new Error("error");
    return response.json();
  };
  const first = await load(1);
  const records = [...first.items];
  // Bound concurrency while collecting every page, not just the first 50.
  for (let start = 2; start <= first.totalPages; start += 4) {
    const batch = await Promise.all(Array.from({ length: Math.min(4, first.totalPages - start + 1) }, (_, i) => load(start + i)));
    records.push(...batch.flatMap(result => result.items));
  }
  return [...new Map(records.map(item => [item.id, item])).values()];
}

/** Japan marketplace offers grouped by verified work or identical listing title. */
export default function JapanMarket() {
  const { t } = usePreferences();
  const offers = useLoader(loadJapanOffers, []);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  // Search aliases come from MuseBooks' own model records: the API matches every
  // recorded name variant, and each match contributes its display, original and English names.
  const matches = useResource(search ? `/v1/models?${new URLSearchParams({ q: search, pageSize: "10" })}` : "");
  const aliases = useMemo(() => {
    const names = (matches.data?.items || []).map(model => [model.name, model.originalName, model.englishName, ...(model.aliases || "").split(",")].map(name => name?.trim()).filter(Boolean));
    return aliasIndex(names.map(list => [search, ...list]));
  }, [matches.data, search]);
  const [format, setFormat] = useState("");
  const [availability, setAvailability] = useState("");
  const [sortBy, setSortBy] = useState("observed");
  const [page, setPage] = useState(1);
  useEffect(() => setPage(1), [search, format, availability, sortBy]);
  const groups = useMemo(() => {
    const result = marketplaceGroups(offers.data || [], { query: search, format, availability, aliases });
    // Unmatched records have no verified publication date; keep observation order otherwise.
    return sortBy === "title" ? result.sort((a, b) => a.title.localeCompare(b.title)) : result;
  }, [offers.data, search, format, availability, sortBy, aliases]);
  const offerCount = groups.reduce((count, group) => count + group.items.length, 0);
  return <div className="japan-market">
    <div className="toolbar toolbar--wrap">
      <form className="search-field" role="search" onSubmit={event => { event.preventDefault(); setSearch(query.trim()); }}>
        <Icon name="search" size={18} />
        <input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder={t("Title or model name")} aria-label={t("Search Japan marketplace")} />
        <button type="submit" className="button">{t("Search")}</button>
      </form>
      <label className="select-field"><span>{t("Format")}</span><select value={format} onChange={event => setFormat(event.target.value)}><option value="">{t("All formats")}</option><option value="physical">{t("Physical")}</option><option value="digital">{t("Digital")}</option></select></label>
      <label className="select-field"><span>{t("Status")}</span><select value={availability} onChange={event => setAvailability(event.target.value)}><option value="">{t("All records")}</option><option value="active">{t("Active")}</option><option value="completed">{t("Completed")}</option></select></label>
      <label className="select-field"><span>{t("Sort by")}</span><select value={sortBy} onChange={event => setSortBy(event.target.value)}><option value="observed">{t("Latest observed")}</option><option value="title">{t("Title")}</option></select></label>
    </div>
    <LoadState state={offers.state} retry={offers.retry} errorMessage="Japan marketplace records could not be loaded." loadingMessage="Loading marketplace offers…" />
    {offers.state === "live" && <>
      <p className="results-count" role="status">{groups.length.toLocaleString()} {t("title groups")} · {offerCount.toLocaleString()} {t("offers")}</p>
      {!groups.length && <p className="load-state">{t("No Japan marketplace listings match these filters.")}</p>}
      <div className="offer-grid">{groups.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map(group => <article className="offer-card" key={group.key}>
        {showCatalogImages && <div className="offer-card__image">{group.imageUrl ? <img src={group.imageUrl} alt="" loading="lazy" /> : <span>{t("Photo unavailable")}</span>}</div>}
        <div className="offer-card__body">
          <p className={`status-tag${group.workSlug ? " status-tag--ok" : ""}`}>{t(group.workSlug ? "Catalog matched" : "Catalog match pending")}</p>
          <h3>{group.workSlug ? <a href={`/books/${encodeURIComponent(group.workSlug)}`}>{group.title}</a> : group.title}</h3>
          {group.formats.map(itemFormat => {
            const offer = group.items.find(item => (item.format || "physical") === itemFormat);
            return <div className="offer-card__price" key={itemFormat}>
              <span>{t(itemFormat === "digital" ? "Digital edition" : "Physical book")}{offer.releaseDate ? ` · ${offer.releaseDate.slice(0, offer.releasePrecision === "month" ? 7 : offer.releasePrecision === "year" ? 4 : 10)}` : ""}</span>
              <strong>{formatPrice(offer.priceMinor, offer.currency)}<small>{t(itemFormat === "digital" ? "Digital retail price" : offer.priceType === "auction_current" ? "Current bid" : offer.status === "completed" ? "Sold price" : "Asking price")}</small></strong>
            </div>;
          })}
          <details><summary>{t("Prices by platform")} · {group.items.length} {t(group.items.length === 1 ? "offer" : "offers")}</summary>
            {group.formats.map(itemFormat => <EditionPrices key={itemFormat} edition={{ editionLabel: group.title, format: itemFormat, listings: group.items.filter(item => (item.format || "physical") === itemFormat).map(item => ({ ...item, format: itemFormat, source: { ...item.source, photobookFormat: itemFormat } })) }} />)}
          </details>
        </div>
      </article>)}</div>
      <Pagination page={page} pages={Math.ceil(groups.length / PAGE_SIZE)} onPage={next => { setPage(next); window.scrollTo(0, 0); }} label="Marketplace results pages" />
    </>}
  </div>;
}
