import { useEffect, useState } from "react";
import { apiUrl } from "./api";

// Session-level request cache: Discover, Browse and Saved share one catalog load.
const cache = new Map();

async function getJSON(path, signal) {
  const response = await fetch(apiUrl(path), { signal });
  if (!response.ok) throw new Error(response.status === 404 ? "missing" : "error");
  return response.json();
}

function cached(key, load) {
  if (!cache.has(key)) cache.set(key, load().catch(error => { cache.delete(key); throw error; }));
  return cache.get(key);
}

async function loadAllPages(endpoint) {
  const join = endpoint.includes("?") ? "&" : "?";
  const first = await getJSON(`${endpoint}${join}pageSize=50&page=1`);
  const rest = await Promise.all(Array.from({ length: Math.max(0, first.totalPages - 1) }, (_, index) => getJSON(`${endpoint}${join}pageSize=50&page=${index + 2}`)));
  return [first, ...rest].flatMap(result => result.items);
}

export const loadAllBooks = () => cached("books", () => loadAllPages("/v1/books"));
export const loadOrigins = () => cached("origins", () => getJSON("/v1/origins"));
export const loadSources = () => cached("sources", () => getJSON("/v1/sources").catch(() => []));
/** Total of people credited on published MuseBooks works (the API excludes everyone else). */
export const loadModelTotal = () => cached("model-total", () => getJSON("/v1/models?pageSize=1&page=1").then(result => result.total));

/** Models ranked by photobook credits in the loaded catalog (magazine cover credits excluded). */
export function photobookModels(books) {
  const byId = new Map();
  for (const book of books) {
    if (isMagazine(book)) continue;
    for (const model of book.models || []) {
      if (!model.id) continue;
      const entry = byId.get(model.id) || { id: model.id, name: model.name, workCount: 0, coverUrl: "", latest: 0, works: [] };
      entry.workCount += 1;
      entry.works.push(book.id);
      const released = releaseTimestamp(book);
      if (book.coverUrl && released >= entry.latest) { entry.coverUrl = book.coverUrl; entry.latest = released; }
      byId.set(model.id, entry);
    }
  }
  // Some people exist as two credit records (e.g. Japanese and romanised names) on
  // exactly the same works; show them once, with the other name as an alias.
  const merged = new Map();
  for (const entry of byId.values()) {
    const key = entry.works.sort().join(",");
    const existing = merged.get(key);
    if (!existing) { merged.set(key, { ...entry, alias: "" }); continue; }
    const latin = /^[\x20-\x7E]+$/;
    const [primary, other] = latin.test(entry.name) && !latin.test(existing.name) ? [entry, existing] : [existing, entry];
    merged.set(key, { ...primary, alias: other.name });
  }
  return [...merged.values()].sort((a, b) => b.workCount - a.workCount || a.name.localeCompare(b.name));
}

/** Runs a loader and tracks loading / live / error / missing state with retry. */
export function useLoader(load, deps) {
  const [result, setResult] = useState({ state: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    setResult(current => ({ ...current, state: "loading" }));
    load().then(data => { if (active) setResult({ state: "live", data }); })
      .catch(error => { if (active) setResult({ state: error?.message === "missing" ? "missing" : "error" }); });
    return () => { active = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, attempt]);
  return { ...result, retry: () => setAttempt(value => value + 1) };
}

/** Fetches a single API path (uncached) with abort on change. */
export function useResource(path) {
  const [result, setResult] = useState({ state: "loading" });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!path) { setResult({ state: "idle" }); return undefined; }
    const controller = new AbortController();
    setResult(current => ({ ...current, state: "loading" }));
    getJSON(path, controller.signal).then(data => { if (!controller.signal.aborted) setResult({ state: "live", data }); })
      .catch(error => { if (!controller.signal.aborted) setResult({ state: error.message === "missing" ? "missing" : "error" }); });
    return () => controller.abort();
  }, [path, attempt]);
  return { ...result, retry: () => setAttempt(value => value + 1) };
}

export function getBook(slug) {
  return getJSON(`/v1/books/${encodeURIComponent(slug)}`);
}

export const bookTitle = book => book.englishTitle || book.originalTitle;
export const bookPath = book => `/books/${encodeURIComponent(book.slug)}`;
export const isMagazine = book => book?.publicationType === "magazine_issue";
export const publicationTypeLabel = book => isMagazine(book) ? "Magazine issue" : "Photobook";
export function editionFormatLabel(edition, book) {
  if (isMagazine(book)) return edition?.format === "digital" ? "Digital magazine issue" : "Print magazine issue";
  if (!edition) return "No edition recorded";
  return edition.format === "digital" ? "Digital edition" : "Physical book";
}
export function bookPeople(book) {
  const people = isMagazine(book) ? book.coverModels : book.models;
  return people?.length ? people : (book.featuredNames || []).map(name => ({ name }));
}
export function releaseTimestamp(book) {
  return Math.max(0, ...(book.editions || []).map(item => item.releaseDate ? Date.parse(item.releaseDate) || 0 : 0));
}
export function sortBooks(books, sortBy) {
  const list = [...books];
  if (sortBy === "title") return list.sort((a, b) => bookTitle(a).localeCompare(bookTitle(b)));
  return list.sort((a, b) => {
    const aDate = releaseTimestamp(a); const bDate = releaseTimestamp(b);
    if (!aDate || !bDate) return aDate ? -1 : bDate ? 1 : 0;
    return sortBy === "oldest" ? aDate - bDate : bDate - aDate;
  });
}
export const releaseYear = book => { const time = releaseTimestamp(book); return time ? new Date(time).getFullYear() : ""; };
