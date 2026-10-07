import { useEffect, useState } from "react";
import { apiUrl } from "../lib/api";
import { formatPrice } from "../lib/price-policy";
function useCatalogPage(path) {
    const [data, setData] = useState({ items: [], total: 0, totalPages: 0, page: 1 });
    const [state, setState] = useState("loading");
    const [retry, setRetry] = useState(0);
    useEffect(() => {
        const controller = new AbortController();
        setState("loading");
        fetch(apiUrl(path), { signal: controller.signal }).then(async (response) => { if (!response.ok)
            throw new Error("Catalog unavailable"); return response.json(); })
            .then(result => { if (!controller.signal.aborted) {
            setData(result);
            setState("live");
        } })
            .catch(() => { if (!controller.signal.aborted)
            setState("error"); });
        return () => controller.abort();
    }, [path, retry]);
    return { data, state, retry: () => setRetry(n => n + 1) };
}
function Pagination({ page, pages, onPage }) {
    if (pages < 2)
        return null;
    return <nav className="catalog-pagination" aria-label="Results pages"><button disabled={page <= 1} onClick={() => onPage(page - 1)}>Previous</button><span>Page {page} of {pages}</span><button disabled={page >= pages} onClick={() => onPage(page + 1)}>Next</button></nav>;
}
function State({ state, empty, retry }) {
    if (state === "loading")
        return <p role="status">Loading catalog records…</p>;
    if (state === "error")
        return <div role="alert"><p>These catalog records could not be loaded.</p><button onClick={retry}>Retry connection</button></div>;
    if (empty)
        return <p role="status">No verified records match these filters.</p>;
    return null;
}
function DirectoryBooks({ kind, entry, onBack }) {
    const [page, setPage] = useState(1);
    const { data, state, retry } = useCatalogPage(`/v1/${kind}/${encodeURIComponent(entry.id)}/books?page=${page}`);
    return <><button className="directory-back" onClick={onBack}>Back to {kind}</button><h2>{entry.name}</h2><nav className="directory-market-links" aria-label={`${entry.name} listings`}><a href={`/active?${kind === "models" ? "model" : "publisher"}=${encodeURIComponent(entry.id)}&name=${encodeURIComponent(entry.name)}`}>Active listings</a><a href={`/sold?${kind === "models" ? "model" : "publisher"}=${encodeURIComponent(entry.id)}&name=${encodeURIComponent(entry.name)}`}>Sold listings</a></nav><State state={state} empty={!data.items.length} retry={retry}/>
 {state === "live" && <div className="directory-books">{data.items.map(book => <a className="directory-book" key={book.id} href={`/#${encodeURIComponent(book.slug)}`}>
  {book.coverUrl && <img src={book.coverUrl} loading="lazy" alt=""/>}<div><h3>{book.originalTitle}</h3><p>{book.featuredNames?.join(" · ")}</p><p>{book.editions.map(e => `${e.editionLabel} (${e.format})`).join(" · ")}</p></div>
 </a>)}</div>}<Pagination page={page} pages={data.totalPages} onPage={setPage}/></>;
}
export default function CatalogPages({ section }) {
    useEffect(() => { document.title = `${section === "models" ? "Models" : section === "publishers" ? "Publishers" : section === "active" ? "Active listings" : "Sold listings"} — MuseBooks`; }, [section]);
    const directory = section === "models" || section === "publishers";
    const initial = new URLSearchParams(window.location.search);
    const [query, setQuery] = useState(() => initial.get("q") || "");
    const [search, setSearch] = useState(query);
    const [page, setPage] = useState(1);
    const [format, setFormat] = useState(() => section === "sold" ? "physical" : initial.get("format") || "");
    const [source, setSource] = useState(() => initial.get("source") || "");
    const [selected, setSelected] = useState();
    const [sources, setSources] = useState([]);
    useEffect(() => { const abort = new AbortController(); fetch(apiUrl("/v1/sources"), { signal: abort.signal }).then(r => r.ok ? r.json() : []).then(setSources).catch(() => { }); return () => abort.abort(); }, []);
    const params = new URLSearchParams({ q: search, page: String(page), pageSize: "24" });
    if (!directory) {
        params.set("status", section);
        if (format)
            params.set("format", format);
        if (source)
            params.set("source", source);
    }
    for (const key of ["model", "publisher"]) {
        const value = initial.get(key);
        if (!directory && value)
            params.set(key, value);
    }
    const { data, state, retry } = useCatalogPage(`/v1/${directory ? section : "listings"}?${params}`);
    const heading = section === "models" ? "Models & featured people" : section === "publishers" ? "Publishers" : section === "active" ? "Active listings" : "Sold listings";
    return <section className="catalog-browser" aria-labelledby="browser-title">
  <h1 id="browser-title">{heading}</h1><p className="browser-intro">{directory ? "Explore photobooks through their catalog credits, across physical and digital editions." : section === "sold" ? "Completed physical marketplace sales. Ended offers are kept separate from sold records." : "Available physical and digital offers, with original prices and source links. Availability reflects the last observation."}</p>
  {!directory && (initial.has("model") || initial.has("publisher")) && <p>Listings for {initial.get("name") || "selected catalog credit"} · <a href={`/${section}`}>Show all listings</a></p>}
  {selected && directory ? <DirectoryBooks kind={section} entry={selected} onBack={() => setSelected(undefined)}/> : <>
  <form className="browser-filters" onSubmit={e => { e.preventDefault(); setSearch(query.trim()); setPage(1); }}>
   <label>Search {directory ? section : "listings"}<input value={query} onChange={e => setQuery(e.target.value)} placeholder={directory ? "Search by name" : "Title, person, or publisher"}/></label>
   {!directory && <><label>Format<select value={format} onChange={e => { setFormat(e.target.value); setPage(1); }}><option value="">All formats</option><option value="physical">Physical</option>{section !== "sold" && <option value="digital">Digital</option>}</select></label><label>Source<select value={source} onChange={e => { setSource(e.target.value); setPage(1); }}><option value="">All sources</option>{sources.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}</select></label></>}
   <button type="submit">Search</button>
  </form>
  <State state={state} empty={!data.items.length} retry={retry}/>
  {state === "live" && <><p className="browser-count">{data.total.toLocaleString()} {directory ? data.total === 1 ? "catalog entry" : "catalog entries" : data.total === 1 ? "listing" : "listings"}</p>
   {directory ? <div className="directory-grid">{data.items.map(entry => <button className="directory-entry" key={entry.id} onClick={() => setSelected(entry)}>
    {entry.coverUrl ? <img src={entry.coverUrl} loading="lazy" alt=""/> : <span className="directory-placeholder" aria-hidden="true">{entry.name.slice(0, 1)}</span>}<span><strong>{entry.name}</strong><small>{entry.workCount} photobooks · {entry.editionCount} editions</small></span>
   </button>)}</div> : <div className="listing-scroll" tabIndex={0} role="region" aria-label={heading}><table className="listing-ledger"><thead><tr><th>Photobook / edition</th><th>Source</th><th>{section === "sold" ? "Sold price" : "Offer price"}</th><th>Condition</th><th>Observed</th><th>Links</th></tr></thead><tbody>{data.items.map(item => <tr key={item.id}>
    <td><strong>{item.workTitle}</strong><small>{item.featuredNames?.join(" · ")}</small><small>{item.editionLabel} · {item.format}</small>{item.publisher && <small>{item.publisher}</small>}</td><td>{item.source.name}<small>{item.source.region}</small></td><td className="listing-price">{formatPrice(item.priceMinor, item.currency)}<small>{section === "sold" ? "Completed sale" : item.priceType === "auction_current" ? "Current bid" : item.priceCategory?.includes("retail") ? "Retail asking price" : "Asking price"}</small></td><td>{item.condition || "Not recorded"}<small>{item.shippingText}</small></td><td>{item.observedAt ? <time dateTime={item.observedAt}>{new Date(item.observedAt).toLocaleDateString()}</time> : "Not recorded"}</td><td><a href={`/#${encodeURIComponent(item.workSlug)}`}>Book details</a><a href={item.url} target="_blank" rel="noreferrer" data-external-link>View source ↗</a></td>
   </tr>)}</tbody></table></div>}
   <Pagination page={page} pages={data.totalPages} onPage={setPage}/></>}
  </>}
 </section>;
}
