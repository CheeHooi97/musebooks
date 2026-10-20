import SeoHead from "../components/SeoHead";
import ListingsView from "../components/ListingsView";
import JapanMarket from "../components/JapanMarket";
import { PageHeader, Tabs } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { hasSearchFilters } from "../lib/seo";

const INTROS = {
  active: "Available physical and digital offers, with original prices and source links. Availability reflects the last observation.",
  sold: "Completed physical marketplace sales. Ended offers are kept separate from sold records.",
  japan: "A snapshot of Japanese marketplace listings from Yahoo! JAPAN Auctions, Yahoo! Flea Market, and Rakuma. Prices show the latest captured state: current bids, fixed asks, and completed prices. Bundle prices apply to the whole listing. Unmatched listings stay separate from verified catalog books.",
};

// One Market section; each tab keeps its own indexed URL (/active, /sold, /japan).
export default function Market({ tab, search }) {
  const { t } = usePreferences();
  const params = new URLSearchParams(search);
  const scope = { model: params.get("model") || "", publisher: params.get("publisher") || "", name: params.get("name") || "" };
  const scoped = scope.model || scope.publisher;
  return <div className="page-width">
    <SeoHead path={`/${tab}`} noindex={hasSearchFilters(search)} />
    <PageHeader eyebrow={t("Market")} title={t("Prices & listings")} intro={t(INTROS[tab])} />
    <Tabs label={t("Market sections")} current={tab} items={[["active", t("For sale"), "/active"], ["sold", t("Sold"), "/sold"], ["japan", t("Japan marketplace"), "/japan"]]} />
    {scoped && tab !== "japan" && <p className="scope-note">{t("Listings for")} <strong>{scope.name || t("selected catalog credit")}</strong> · <a className="text-link" href={`/${tab}`}>{t("Show all listings")}</a></p>}
    {tab === "japan" ? <JapanMarket /> : <ListingsView key={tab} status={tab} scope={scope} syncUrl />}
  </div>;
}
