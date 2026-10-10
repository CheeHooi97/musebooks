import { useEffect, useMemo, useState } from "react";
import { apiUrl } from "../lib/api";
import { usePreferences } from "../lib/preferences";
import { showCatalogImages } from "../lib/platform";
import { marketplaceGroups } from "../lib/marketplace-groups";
import { formatPrice } from "../lib/price-policy";
import EditionPrices from "./EditionPrices";

export default function HomeMarketplace({ query, format, availability, sortBy, onTotal }) {
  const { t } = usePreferences();
  const [items, setItems] = useState([]);
  const [state, setState] = useState("loading");
  const [retry, setRetry] = useState(0);
  const [page, setPage] = useState(1);
  useEffect(() => {
    const controller = new AbortController();
    setState("loading");
    const load = async page => {
      const response = await fetch(apiUrl(`/v1/marketplace-listings?region=JP&status=all&pageSize=50&page=${page}`), { signal: controller.signal });
      if (!response.ok) throw new Error("Marketplace unavailable");
      return response.json();
    };
    (async () => {
      const first = await load(1);
      const records = [...first.items];
      // Bound concurrency while collecting every page, not just the first 50.
      for (let start = 2; start <= first.totalPages; start += 4) {
        const batch = await Promise.all(Array.from({ length: Math.min(4, first.totalPages - start + 1) }, (_, i) => load(start + i)));
        records.push(...batch.flatMap(result => result.items));
      }
      const unique = [...new Map(records.map(item => [item.id, item])).values()];
      if (!controller.signal.aborted) { setItems(unique); onTotal(unique.length); setState("live"); }
    })().catch(() => { if (!controller.signal.aborted) setState("error"); });
    return () => controller.abort();
  }, [retry, onTotal]);
  useEffect(() => setPage(1), [query, format, availability, sortBy]);
  const groups = useMemo(() => {
    const result = marketplaceGroups(items, { query, format, availability });
    // Unmatched records have no verified publication date. Keep observation
    // order for release sorting rather than inventing a release date.
    return sortBy === "title" ? result.sort((a, b) => a.title.localeCompare(b.title)) : result;
  }, [items, query, format, availability, sortBy]);
  const pages = Math.ceil(groups.length / 24);
  return <section className="home-marketplace" aria-labelledby="home-marketplace-title">
    <h2 id="home-marketplace-title">{t("Japan marketplace listings")}</h2>
    <p>{t("Marketplace offers are grouped by verified book or identical listing title. Unmatched titles and bundles are awaiting catalog matching. Bundle prices apply to the whole listing.")}</p>
    {state === "loading" && <p role="status">{t("Loading marketplace offers…")}</p>}
    {state === "error" && <div role="alert"><p>{t("Japan marketplace records could not be loaded.")}</p><button onClick={() => setRetry(value => value + 1)}>{t("Retry connection")}</button></div>}
    {state === "live" && <>
      <p role="status">{groups.length} {t("title groups")} · {groups.reduce((count, group) => count + group.items.length, 0)} {t("offers")}</p>
      {!groups.length && <p>{t("No Japan marketplace listings match these filters.")}</p>}
      <div className="japan-marketplace-grid">{groups.slice((page - 1) * 24, page * 24).map(group => <article className="japan-marketplace-entry" key={group.key}>
        {showCatalogImages && group.imageUrl && <div className="japan-marketplace-entry__image"><img src={group.imageUrl} alt={group.title} loading="lazy" /></div>}
        <h3>{group.workSlug ? <a href={`/books/${encodeURIComponent(group.workSlug)}`}>{group.title}</a> : group.title}</h3>
        <p>{t(group.workSlug ? "Catalog matched" : "Catalog match pending")}</p>
        <p className="japan-marketplace-entry__price">{formatPrice(group.items[0].priceMinor, group.items[0].currency)}<small>{t(group.items[0].priceType === "auction_current" ? "Current bid" : group.items[0].status === "completed" ? "Sold price" : "Asking price")}</small></p>
        <details><summary>{t("Prices by platform")} · {group.items.length} {t("offers")}</summary>
          <EditionPrices edition={{ editionLabel: group.title, format: "physical", listings: group.items.map(item => ({ ...item, format: item.format || "physical", source: { ...item.source, photobookFormat: item.format || "physical" } })) }} />
        </details>
      </article>)}</div>
      {pages > 1 && <nav className="catalog-pagination" aria-label={t("Marketplace results pages")}><button disabled={page <= 1} onClick={() => setPage(value => value - 1)}>{t("Previous")}</button><span>{t("Page")} {page} {t("of")} {pages}</span><button disabled={page >= pages} onClick={() => setPage(value => value + 1)}>{t("Next")}</button></nav>}
    </>}
  </section>;
}
