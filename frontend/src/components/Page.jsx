import { usePreferences } from "../lib/preferences";

export function PageHeader({ eyebrow, title, intro, children, id = "page-title" }) {
  return <header className="page-header">
    <div className="page-header__copy">
      {eyebrow && <p className="eyebrow">{eyebrow}</p>}
      <h1 id={id} tabIndex={-1}>{title}</h1>
      {intro && <p className="page-header__intro">{intro}</p>}
    </div>
    {children}
  </header>;
}

export function Breadcrumb({ items }) {
  const { t } = usePreferences();
  return <nav className="breadcrumb" aria-label={t("Breadcrumb")}>
    {items.map(([label, href], index) => <span key={`${label}-${index}`}>{href ? <a href={href}>{label}</a> : <span aria-current="page">{label}</span>}</span>)}
  </nav>;
}

export function SectionHeading({ title, id, action, href, count }) {
  return <div className="section-heading">
    <h2 id={id}>{title}{count !== undefined && <span className="section-heading__count">{count}</span>}</h2>
    {action && href && <a href={href} className="text-link">{action}</a>}
  </div>;
}

/** Loading, error and empty states for API-backed sections. */
export function LoadState({ state, retry, empty, emptyMessage = "No verified records match these filters.", errorMessage = "These catalog records could not be loaded.", loadingMessage = "Loading catalog records…" }) {
  const { t } = usePreferences();
  if (state === "loading") return <p className="load-state" role="status">{t(loadingMessage)}</p>;
  if (state === "error" || state === "missing") return <div className="load-state load-state--error" role="alert"><p>{t(state === "missing" ? "Catalog profile not found." : errorMessage)}</p>{state === "error" && retry && <button type="button" className="button" onClick={retry}>{t("Retry connection")}</button>}</div>;
  if (empty) return <p className="load-state" role="status">{t(emptyMessage)}</p>;
  return null;
}

export function Pagination({ page, pages, onPage, label = "Results pages" }) {
  const { t } = usePreferences();
  if (pages < 2) return null;
  return <nav className="pagination" aria-label={t(label)}>
    <button type="button" className="button button--ghost" disabled={page <= 1} onClick={() => onPage(page - 1)}>{t("Previous")}</button>
    <span>{t("Page")} {page} {t("of")} {pages}</span>
    <button type="button" className="button button--ghost" disabled={page >= pages} onClick={() => onPage(page + 1)}>{t("Next")}</button>
  </nav>;
}

export function Tabs({ items, current, label }) {
  return <nav className="tabs" aria-label={label}>
    {items.map(([key, text, href]) => <a key={key} href={href} className={key === current ? "is-active" : ""} aria-current={key === current ? "page" : undefined}>{text}</a>)}
  </nav>;
}
