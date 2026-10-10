import DirectoryProfile from "./DirectoryProfile";
import { showCatalogImages } from "../lib/platform";
import { usePreferences } from "../lib/preferences";import { useEffect, useState } from "react";
import { apiUrl } from "../lib/api";
import "../lib/price-policy";
function useCatalogPage(path) {
  const [data, setData] = useState({ items: [], total: 0, totalPages: 0, page: 1 });
  const [state, setState] = useState("loading");
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setState("loading");
    fetch(apiUrl(path), { signal: controller.signal }).then(async (response) => {if (!response.ok)
      throw new Error("Catalog unavailable");return response.json();}).
    then((result) => {if (!controller.signal.aborted) {
        setData(result);
        setState("live");
      }}).
    catch(() => {if (!controller.signal.aborted)
      setState("error");});
    return () => controller.abort();
  }, [path, retry]);
  return { data, state, retry: () => setRetry((n) => n + 1) };
}
function Pagination({ page, pages, onPage }) {const { t, formatPrice } = usePreferences();
  if (pages < 2)
  return null;
  return <nav className="catalog-pagination" aria-label={t("Results pages")}><button disabled={page <= 1} onClick={() => onPage(page - 1)}>{t("Previous")}</button><span>{t("Page")}{page}{t("of")}{pages}</span><button disabled={page >= pages} onClick={() => onPage(page + 1)}>{t("Next")}</button></nav>;
}
function State({ state, empty, retry, emptyMessage = "No verified records match these filters.", errorMessage = "These catalog records could not be loaded." }) {const { t, formatPrice } = usePreferences();
  if (state === "loading")
  return <p role="status">{t("Loading catalog records\u2026")}</p>;
  if (state === "error")
  return <div role="alert"><p>{t(errorMessage)}</p><button onClick={retry}>{t("Retry connection")}</button></div>;
  if (empty)
  return <p role="status">{t(emptyMessage)}</p>;
  return null;
}
export default function CatalogPages({ section }) {const { t, formatPrice } = usePreferences();
  const directory = section === "models" || section === "publishers";
  const japanListings = section === "japan";
  const initial = new URLSearchParams(window.location.search);
  const [query, setQuery] = useState(() => initial.get("q") || "");
  const [search, setSearch] = useState(query);
  const [page, setPage] = useState(1);
  const [format, setFormat] = useState(() => section === "sold" ? "physical" : initial.get("format") || "");
  const [source, setSource] = useState(() => initial.get("source") || "");
  const [status, setStatus] = useState(() => initial.get("status") || "all");
  const profileId = window.location.pathname.split("/")[2];
  const [sources, setSources] = useState([]);
  useEffect(() => {const abort = new AbortController();fetch(apiUrl("/v1/sources"), { signal: abort.signal }).then((r) => r.ok ? r.json() : []).then(setSources).catch(() => {});return () => abort.abort();}, []);
  const params = new URLSearchParams({ q: search, page: String(page), pageSize: "24" });
  if (!directory) {
    params.set("status", japanListings ? status : section);
    if (japanListings)
    params.set("region", "JP");
    if (format && !japanListings)
    params.set("format", format);
    if (source)
    params.set("source", source);
  }
  for (const key of ["model", "publisher"]) {
    const value = initial.get(key);
    if (!directory && value)
    params.set(key, value);
  }
  const endpoint = directory ? section : japanListings ? "marketplace-listings" : "listings";
  const { data, state, retry } = useCatalogPage(`/v1/${endpoint}?${params}`);
  const heading = section === "models" ? "Models & featured people" : section === "publishers" ? "Publishers" : section === "active" ? "Active listings" : section === "sold" ? "Sold listings" : "Japan marketplace listings";
  return <section className="catalog-browser" aria-labelledby="browser-title">
  {!profileId && <><h1 id="browser-title">{t(heading)}</h1><p className="browser-intro">{directory ? t("Explore photobooks through their catalog credits, across physical and digital editions.") : japanListings ? t("A snapshot of Japanese marketplace listings from Yahoo! JAPAN Auctions, Yahoo! Flea Market, and Rakuma. Prices show the latest captured state: current bids, fixed asks, and completed prices. Bundle prices apply to the whole listing. Unmatched listings stay separate from verified catalog books.") : section === "sold" ? t("Completed physical marketplace sales. Ended offers are kept separate from sold records.") : t("Available physical and digital offers, with original prices and source links. Availability reflects the last observation.")}</p></>}
  {!directory && (initial.has("model") || initial.has("publisher")) && <p>{t("Listings for")}{initial.get("name") || "selected catalog credit"} · <a href={`/${section}`}>{t("Show all listings")}</a></p>}
  {profileId && directory ? <DirectoryProfile kind={section} id={profileId} /> : <>
  <form className="browser-filters" onSubmit={(e) => {e.preventDefault();setSearch(query.trim());setPage(1);}}>
   <label>{t("Search")} {directory ? section : t(japanListings ? "Japan marketplace listings" : "listings")}<input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={directory ? t("Search by name") : t("Title, person, or publisher")} /></label>
   {!directory && <>{japanListings && <label>{t("Status")}<select value={status} onChange={(e) => {setStatus(e.target.value);setPage(1);}}><option value="all">{t("All records")}</option><option value="active">{t("Active")}</option><option value="completed">{t("Completed")}</option></select></label>}{!japanListings && <label>{t("Format")}<select value={format} onChange={(e) => {setFormat(e.target.value);setPage(1);}}><option value="">{t("All formats")}</option><option value="physical">{t("Physical")}</option>{section !== "sold" && <option value="digital">{t("Digital")}</option>}</select></label>}<label>{t("Source")}<select value={source} onChange={(e) => {setSource(e.target.value);setPage(1);}}><option value="">{t("All sources")}</option>{sources.filter((s) => !japanListings || s.region === "JP").map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</select></label></>}
   <button type="submit">{t("Search")}</button>
  </form>
  <State state={state} empty={!data.items.length} retry={retry} emptyMessage={japanListings ? "No Japan marketplace listings match these filters." : undefined} errorMessage={japanListings ? "Japan marketplace records could not be loaded." : undefined} />
  {state === "live" && <><p className="browser-count">{data.total.toLocaleString()} {directory ? data.total === 1 ? t("catalog entry") : t("catalog entries") : data.total === 1 ? t("listing") : t("listings")}</p>
   {directory ? <div className="directory-grid">{data.items.map((entry) => <a className="directory-entry" key={entry.id} href={`/${section}/${encodeURIComponent(entry.id)}`}>
    {showCatalogImages && (entry.coverUrl ? <img src={entry.coverUrl} loading="lazy" alt="" /> : <span className="directory-placeholder" aria-hidden="true">{entry.name.slice(0, 1)}</span>)}<span><strong>{entry.name}</strong><small>{entry.workCount} {t("photobooks")} · {entry.editionCount} {t("editions")}</small></span>
   </a>)}</div> : japanListings ? <div className="japan-marketplace-grid" aria-label={t(heading)}>{data.items.map((item) => <article className="japan-marketplace-entry" key={item.id}>
    <a className="japan-marketplace-entry__image" href={item.url} target="_blank" rel="noreferrer" data-external-link aria-label={`${t("View source")}: ${item.title}`}>
     {showCatalogImages && item.imageUrl ? <img src={item.imageUrl} loading="lazy" alt={item.title} /> : <span aria-hidden="true">{t("Photo unavailable")}</span>}
    </a>
    <div className="japan-marketplace-entry__body">
     <div className="japan-marketplace-entry__status"><span>{item.status === "completed" ? t("Completed") : item.status === "active" ? t("Active") : t("Status unverified")}</span><span>{item.catalogMatched ? t("Catalog matched") : t("Catalog match pending")}</span></div>
     <h2>{item.workTitle || item.title}</h2>
     {item.workTitle && <p className="japan-marketplace-entry__source-title">{item.title}</p>}
     <p className="japan-marketplace-entry__source">{item.source.name}{item.sellerLocation ? ` · ${item.sellerLocation}` : ""}</p>
     <div className="japan-marketplace-entry__price">{formatPrice(item.priceMinor, item.currency)}<small>{item.priceType === "auction_current" ? t("Current bid") : item.status === "completed" ? t("Completed price") : t("Fixed asking price")}</small></div>
     <p className="japan-marketplace-entry__condition">{item.condition || t("Condition not recorded")}{item.shippingText ? ` · ${item.shippingText}` : ""}</p>
     <time dateTime={item.observedAt}>{t("Observed")}: {item.observedAt ? new Date(item.observedAt).toLocaleDateString() : t("Not recorded")}</time>
     <div className="japan-marketplace-entry__links">{item.catalogMatched && item.workSlug && <a href={`/books/${encodeURIComponent(item.workSlug)}`}>{t("Book details")}</a>}<a href={item.url} target="_blank" rel="noreferrer" data-external-link>{t("View source ↗")}</a></div>
    </div>
   </article>)}</div> : <div className="listing-scroll" tabIndex={0} role="region" aria-label={t(heading)}><table className="listing-ledger"><thead><tr><th>{t("Photobook / edition")}</th><th>{t("Source")}</th><th>{section === "sold" ? t("Sold price") : t("Offer price")}</th><th>{t("Condition")}</th><th>{t("Observed")}</th><th>{t("Links")}</th></tr></thead><tbody>{data.items.map((item) => <tr key={item.id}>
    <td><strong>{item.workTitle}</strong><small>{item.featuredNames?.join(" · ")}</small><small>{item.editionLabel} · {item.format}</small>{item.publisher && <small>{item.publisher}</small>}</td><td>{item.source.name}<small>{item.source.region}</small></td><td className="listing-price">{formatPrice(item.priceMinor, item.currency)}<small>{section === "sold" ? t("Completed sale") : item.priceType === "auction_current" ? t("Current bid") : item.priceCategory?.includes("retail") ? t("Retail asking price") : t("Asking price")}</small></td><td>{item.condition || "Not recorded"}<small>{item.shippingText}</small></td><td>{item.observedAt ? <time dateTime={item.observedAt}>{new Date(item.observedAt).toLocaleDateString()}</time> : t("Not recorded")}</td><td><a href={`/books/${encodeURIComponent(item.workSlug)}`}>{t("Book details")}</a><a href={item.url} target="_blank" rel="noreferrer" data-external-link>{t("View source \u2197")}</a></td>
   </tr>)}</tbody></table></div>}
   <Pagination page={page} pages={data.totalPages} onPage={setPage} /></>}
  </>}
 </section>;
}
