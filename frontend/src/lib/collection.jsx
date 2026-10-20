import { createContext, useContext, useEffect, useMemo, useState } from "react";

// Device-local state shared by every page: the saved collection and the theme.
const SAVED_KEY = "musebooks.collection.v1";
const THEME_KEY = "musebooks.theme.v1";
const Collection = createContext(null);

function readSaved() {
  try {
    const parsed = JSON.parse(window.localStorage.getItem(SAVED_KEY) || "[]");
    return Array.isArray(parsed) ? parsed.filter(item => typeof item === "string") : [];
  } catch { return []; }
}
function readTheme() {
  try {
    const saved = window.localStorage.getItem(THEME_KEY);
    if (saved === "light" || saved === "dark") return saved;
  } catch { /* fall through to the system preference */ }
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function CollectionProvider({ children }) {
  const [saved, setSaved] = useState(readSaved);
  const [theme, setTheme] = useState(readTheme);
  useEffect(() => {
    try { window.localStorage.setItem(SAVED_KEY, JSON.stringify(saved)); } catch { /* best effort */ }
  }, [saved]);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", theme === "dark" ? "#0f0f0f" : "#ffffff");
    try { window.localStorage.setItem(THEME_KEY, theme); } catch { /* theme still applies this visit */ }
  }, [theme]);
  useEffect(() => {
    const sync = event => { if (event.key === SAVED_KEY) setSaved(readSaved()); };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);
  const value = useMemo(() => ({
    saved,
    isSaved: id => saved.includes(id),
    toggleSaved: id => id && setSaved(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id]),
    theme,
    toggleTheme: () => setTheme(current => current === "light" ? "dark" : "light"),
  }), [saved, theme]);
  return <Collection.Provider value={value}>{children}</Collection.Provider>;
}

export function useCollection() {
  const value = useContext(Collection);
  if (!value) throw new Error("useCollection must be used inside CollectionProvider");
  return value;
}
