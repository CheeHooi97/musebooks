import { useEffect } from "react";
import HeaderControls from "./HeaderControls";
import Icon from "./Icon";
import { BannerAds } from "./BannerAds";
import { WebsiteAds } from "./WebsiteAds";
import { usePreferences } from "../lib/preferences";
import { useCollection } from "../lib/collection";
import { isMobileApp } from "../lib/platform";
import { interceptLinks, navigate, runBackHandler } from "../lib/router";
import { languageAlternates } from "../lib/catalog-languages";
import Logo from "./Logo";

// Top-level sections. `match` decides which nav item is current for a path.
export const SECTIONS = [
  { key: "discover", label: "Discover", href: "/", icon: "home", match: path => path === "/" },
  { key: "browse", label: "Browse", href: "/books", icon: "grid", match: path => path.startsWith("/books") },
  { key: "models", label: "Models", href: "/models", icon: "person", match: path => path.startsWith("/models") },
  { key: "publishers", label: "Publishers", href: "/publishers", icon: "book", match: path => path.startsWith("/publishers") },
  { key: "market", label: "Market", href: "/active", icon: "tag", match: path => ["/active", "/sold", "/japan"].includes(path) },
];
const APP_TABS = [...SECTIONS.filter(section => section.key !== "publishers"), { key: "saved", label: "Saved", href: "/saved", icon: "bookmark", match: path => path === "/saved" }];

function useNativeShell() {
  useEffect(() => {
    if (!isMobileApp) return undefined;
    const openExternal = event => {
      const link = event.target instanceof Element ? event.target.closest("a[data-external-link]") : null;
      if (!link) return;
      event.preventDefault();
      import("@capacitor/browser").then(({ Browser }) => Browser.open({ url: link.href })).catch(() => window.open(link.href, "_blank", "noopener,noreferrer"));
    };
    document.addEventListener("click", openExternal);
    let removeBack;
    let cancelled = false;
    import("@capacitor/app").then(({ App }) => App.addListener("backButton", ({ canGoBack }) => {
      if (runBackHandler()) return;
      if (canGoBack) window.history.back();
      else if (window.location.pathname !== "/") navigate("/", { replace: true });
      else App.exitApp();
    })).then(handle => { if (cancelled) handle.remove(); else removeBack = () => handle.remove(); }).catch(() => undefined);
    return () => { cancelled = true; document.removeEventListener("click", openExternal); removeBack?.(); };
  }, []);
}

export default function SiteLayout({ pathname, children, showAds = true }) {
  const { t } = usePreferences();
  const { saved } = useCollection();
  useNativeShell();
  useEffect(() => {
    document.addEventListener("click", interceptLinks);
    return () => document.removeEventListener("click", interceptLinks);
  }, []);
  return <div className={`site-shell${isMobileApp ? " is-app" : ""}`}>
    <a className="skip-link" href="#main-content">{t("Skip to content")}</a>
    <header className="site-header">
      <div className="site-header__inner">
        <a className="wordmark" href="/" aria-label={t("MuseBooks home")}><Logo /></a>
        <nav className="main-nav" aria-label={t("Main navigation")}>
          {SECTIONS.map(section => <a key={section.key} href={section.href} className={section.match(pathname) ? "is-active" : ""} aria-current={section.match(pathname) ? "page" : undefined}>{t(section.label)}</a>)}
        </nav>
        <HeaderControls />
      </div>
    </header>
    <main id="main-content" tabIndex={-1}>
      {children}
      {showAds && <div className="page-width"><BannerAds /><WebsiteAds /></div>}
    </main>
    <footer className="site-footer">
      <div className="site-footer__inner">
        {!isMobileApp && <nav aria-label="Languages">{languageAlternates(pathname, "").filter(item => item.code !== "x-default").map(item => <a key={item.code} href={item.url} lang={item.code} hrefLang={item.code} data-reload>{item.label}</a>)}</nav>}
        <div className="site-footer__brand">
          <a className="wordmark" href="/"><Logo /></a>
          <p>{t("A source-backed catalog of model, idol and entertainer photobooks. Every edition keeps its own record; every price keeps its source.")}</p>
        </div>
        <nav aria-label={t("Catalog")}>
          <h2>{t("Catalog")}</h2>
          <a href="/books">{t("Browse all")}</a><a href="/models">{t("Models")}</a><a href="/publishers">{t("Publishers")}</a><a href="/saved">{t("Saved collection")}</a>
        </nav>
        <nav aria-label={t("Market")}>
          <h2>{t("Market")}</h2>
          <a href="/active">{t("For sale")}</a><a href="/sold">{t("Sold")}</a><a href="/japan">{t("Japan marketplace")}</a>
        </nav>
        <nav aria-label={t("MuseBooks")}>
          <h2>MuseBooks</h2>
          <a href="/guides/digital-vs-physical-photobooks">{t("Digital and physical photobooks")}</a><a href="/about">{t("About & methodology")}</a><a href="/privacy-policy">{t("Privacy Policy")}</a><a href="mailto:musecards67@gmail.com">{t("Send a correction")}</a>
        </nav>
      </div>
    </footer>
    {isMobileApp && <nav className="app-tabbar" aria-label={t("App navigation")}>
      {APP_TABS.map(tab => <a key={tab.key} href={tab.href} className={tab.match(pathname) ? "is-active" : ""} aria-current={tab.match(pathname) ? "page" : undefined}>
        <span className="app-tabbar__icon"><Icon name={tab.icon} size={22} />{tab.key === "saved" && saved.length > 0 && <i>{saved.length}</i>}</span>
        <span>{t(tab.label)}</span>
      </a>)}
    </nav>}
  </div>;
}
