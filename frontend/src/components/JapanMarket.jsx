import { useEffect, useMemo, useRef, useState } from "react";
import Icon from "./Icon";
import EditionPrices from "./EditionPrices";
import { LoadState } from "./Page";
import { apiUrl } from "../lib/api";
import { usePreferences } from "../lib/preferences";
import { showCatalogImages } from "../lib/platform";
import { aliasIndex, marketplaceGroups } from "../lib/marketplace-groups";
import { formatPrice } from "../lib/price-policy";
import { useResource } from "../lib/catalog";

const PAGE_SIZE = 24;
const API_PAGE_SIZE = 50;

async function loadJapanOffers({ cursor = "", search, format, availability, sortBy, signal }) {
  const params = new URLSearchParams({ region: "JP", scope: "offers", status: availability || "all", limit: String(API_PAGE_SIZE), sort: sortBy });
  if (search) params.set("q", search);
  if (format) params.set("format", format);
  if (cursor) params.set("cursor", cursor);
  const response = await fetch(apiUrl(`/v1/marketplace-listings?${params}`), { signal });
  if (!response.ok) throw new Error("error");
  return response.json();
}

async function loadGroupsThroughPage({ data, page, search, format, availability, sortBy, aliases, signal }) {
  let groups = marketplaceGroups(data.items || [], { query: search, format, availability, aliases });
  while (groups.length < page * PAGE_SIZE && data.nextCursor) {
    const next = await loadJapanOffers({ cursor: data.nextCursor, search, format, availability, sortBy, signal });
    data = { ...data, items: [...data.items, ...(next.items || [])], total: next.total, hasMore: next.hasMore, nextCursor: next.nextCursor };
    groups = marketplaceGroups(data.items, { query: search, format, availability, aliases });
  }
  return { data, groups };
}

/** Japan marketplace offers grouped by verified work or identical listing title. */
export default function JapanMarket() {
  const { t } = usePreferences();
  const [offers, setOffers] = useState({ state: "loading" });
  const [attempt, setAttempt] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);
  const [moreError, setMoreError] = useState(false);
  const generation = useRef(0);
  const moreController = useRef(null);
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
  useEffect(() => {
    generation.current += 1;
    const controller = new AbortController();
    moreController.current?.abort();
    moreController.current = null;
    setPage(1);
    setLoadingMore(false);
    setMoreError(false);
    setOffers({ state: "loading" });
    loadJapanOffers({ search, format, availability, sortBy, signal: controller.signal })
      .then(data => loadGroupsThroughPage({ data, page: 1, search, format, availability, sortBy, aliases, signal: controller.signal }))
      .then(({ data }) => { if (!controller.signal.aborted) setOffers({ state: "live", data }); })
      .catch(() => { if (!controller.signal.aborted) setOffers({ state: "error" }); });
    return () => controller.abort();
  }, [search, format, availability, sortBy, aliases, attempt]);
  const groups = useMemo(() => {
    return marketplaceGroups(offers.data?.items || [], { query: search, format, availability, aliases });
  }, [offers.data?.items, search, format, availability, aliases]);
  const offerCount = offers.data?.total ?? 0;
  const hasNextPage = groups.length > page * PAGE_SIZE || Boolean(offers.data?.nextCursor);

  async function goToPage(nextPage) {
    if (loadingMore || moreController.current) return;
    if (nextPage < page) {
      setPage(nextPage);
      window.scrollTo(0, 0);
      return;
    }
    const firstGroup = (nextPage - 1) * PAGE_SIZE;
    const request = generation.current;
    let data = offers.data;
    let loadedGroups = groups;
    if (!data) return;
    if (loadedGroups.length < nextPage * PAGE_SIZE && data.nextCursor) {
      const controller = new AbortController();
      moreController.current = controller;
      setLoadingMore(true);
      setMoreError(false);
      try {
        const loaded = await loadGroupsThroughPage({ data, page: nextPage, search, format, availability, sortBy, aliases, signal: controller.signal });
        if (request !== generation.current || controller.signal.aborted) return;
        data = loaded.data;
        loadedGroups = loaded.groups;
        setOffers({ state: "live", data });
      } catch {
        if (request === generation.current && !controller.signal.aborted) setMoreError(true);
      } finally {
        if (request === generation.current) {
          setLoadingMore(false);
          moreController.current = null;
        }
      }
    }
    if (request === generation.current && loadedGroups.length > firstGroup) {
      setPage(nextPage);
      window.scrollTo(0, 0);
    }
  }

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
    <LoadState state={offers.state} retry={() => setAttempt(value => value + 1)} errorMessage="Japan marketplace records could not be loaded." loadingMessage="Loading marketplace offers…" />
    {offers.state === "live" && <>
      <p className="results-count" role="status">{offers.data.hasMore ? <>{offers.data.items.length.toLocaleString()} {t("of")} {offerCount.toLocaleString()} {t("offers")}</> : <>{groups.length.toLocaleString()} {t("title groups")} · {offerCount.toLocaleString()} {t("offers")}</>}</p>
      {!groups.length && <p className="load-state">{t("No Japan marketplace listings match these filters.")}</p>}
      <div className="offer-grid">{groups.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE).map((group, index) => <article className="offer-card" key={group.key}>
        {showCatalogImages && <div className="offer-card__image">{group.imageUrl ? <img src={group.imageUrl} alt="" loading={index < 2 ? "eager" : "lazy"} fetchPriority={index === 0 ? "high" : "auto"} decoding="async" /> : <span>{t("Photo unavailable")}</span>}</div>}
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
      {moreError && <p className="load-state load-state--error" role="alert">{t("Japan marketplace records could not be loaded.")} <button type="button" className="button" onClick={() => goToPage(page + 1)}>{t("Retry connection")}</button></p>}
      {(page > 1 || hasNextPage) && <nav className="pagination" aria-label={t("Marketplace results pages")}>
        <button type="button" className="button button--ghost" disabled={page <= 1 || loadingMore} onClick={() => goToPage(page - 1)}>{t("Previous")}</button>
        <span>{t("Page")} {page}</span>
        <button type="button" className="button button--ghost" disabled={!hasNextPage || loadingMore} onClick={() => goToPage(page + 1)}>{loadingMore ? t("Loading…") : t("Next")}</button>
      </nav>}
    </>}
  </div>;
}
