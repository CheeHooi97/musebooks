import SiteLayout from "./components/SiteLayout";
import SeoHead from "./components/SeoHead";
import Discover from "./pages/Discover";
import Browse from "./pages/Browse";
import BookPage from "./pages/BookDetail";
import Directory from "./pages/Directory";
import DirectoryProfile from "./pages/DirectoryProfile";
import Market from "./pages/Market";
import Saved from "./pages/Saved";
import About from "./pages/About";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import AuthPage, { AccountPage } from "./pages/Auth";
import { usePreferences } from "./lib/preferences";
import { useLocation } from "./lib/router";

function NotFound() {
  const { t } = usePreferences();
  return <div className="page-width route-state"><SeoHead path="/404" /><p className="eyebrow">404</p><h1>{t("Page not found")}</h1><a className="button" href="/books">{t("Explore photobooks")}</a></div>;
}

function decode(part) {
  try { return decodeURIComponent(part); } catch { return ""; }
}

export function resolveRoute(pathname, search) {
  const [section, id, extra] = pathname.split("/").filter(Boolean);
  if (extra) return { page: <NotFound /> };
  if (!section) return { page: <Discover /> };
  if (section === "books") return id ? { page: <BookPage slug={decode(id)} search={search} /> } : { page: <Browse search={search} /> };
  if (section === "models" || section === "publishers") return id ? { page: <DirectoryProfile kind={section} id={encodeURIComponent(decode(id))} /> } : { page: <Directory kind={section} search={search} /> };
  if (["active", "sold", "japan"].includes(section) && !id) return { page: <Market tab={section} search={search} /> };
  if (section === "saved" && !id) return { page: <Saved />, showAds: false };
  if (["login", "register", "verify-email", "forgot-password", "reset-password"].includes(section) && !id) return { page: <AuthPage mode={section} />, showAds: false };
  if (section === "account" && !id) return { page: <AccountPage />, showAds: false };
  if (section === "about" && !id) return { page: <About /> };
  if (section === "privacy-policy" && !id) return { page: <PrivacyPolicy />, showAds: false };
  return { page: <NotFound />, showAds: false };
}

export default function App() {
  const { pathname, search } = useLocation();
  const { page, showAds = true } = resolveRoute(pathname, search);
  // Keying on the path remounts a page on navigation, so it reads fresh URL state.
  return <SiteLayout pathname={pathname} showAds={showAds}><div key={pathname} className="route">{page}</div></SiteLayout>;
}
