import { usePreferences } from "../lib/preferences";
import { editionListings, formatPrice as nativePrice } from "../lib/price-policy";
import { platformGroups } from "../lib/platform-prices";

export default function EditionPrices({ edition }) {
  const { t } = usePreferences();
  const listings = editionListings(edition);
  const sections = [
    { title: "Retail prices", items: listings.filter(item => item.priceCategory?.endsWith("retail") && item.status !== "ended") },
    { title: "Active marketplace offers", items: listings.filter(item => !item.priceCategory?.endsWith("retail") && item.status === "active") },
    { title: "Confirmed sold prices", items: listings.filter(item => item.priceCategory === "marketplace_sold" && item.status === "completed") },
    { title: "Previous offers", items: listings.filter(item => item.status === "ended" || (item.status === "unknown" && !item.priceCategory?.endsWith("retail"))) },
  ];
  return <section className="platform-comparison" aria-labelledby="platform-prices-title">
    <header className="comparison-heading"><h2 id="platform-prices-title">{t("Prices by platform")}</h2><p>{edition.editionLabel} · {t(edition.format === "digital" ? "Digital edition" : "Physical book")}</p></header>
    <p className="comparison-note">{t("Original currencies. Availability and prices reflect the last recorded observation.")}</p>
    {!listings.length && <p className="comparison-empty" role="status">{t("No platform offers recorded for this edition.")}</p>}
    {sections.filter(section => section.items.length).map(section => <section className="comparison-section" key={section.title}>
      <h3>{t(section.title)}</h3>
      {platformGroups(section.items).map(group => <div className="platform-group" key={group.source.id}>
        <header><h4>{group.source.name}</h4><span>{group.source.region} · {group.items.length} {t(group.items.length === 1 ? "offer" : "offers")}</span></header>
        <div className="platform-offers">{group.items.map(item => <div className="platform-offer" key={item.id}>
          <div className="offer-context"><strong>{item.condition || t("Condition not recorded")}</strong><span>{t(item.status === "completed" ? "Completed sale" : item.status === "ended" ? "Unavailable" : item.status === "active" ? "Available at last check" : "Availability unknown")}{item.sellerLocation && ` · ${item.sellerLocation}`}</span><small>{item.shippingText || t("Shipping and taxes not recorded")}</small>{item.digitalAccess && <small>{item.digitalAccess}</small>}</div>
          <div className="offer-amount"><strong>{item.priceMinor === undefined || !item.currency ? t("Price unavailable") : nativePrice(item.priceMinor, item.currency)}</strong><span>{t(item.priceType === "auction_current" ? "Current bid" : item.status === "completed" ? "Sold price" : "Asking price")}</span><time dateTime={item.observedAt}>{item.observedAt ? new Date(item.observedAt).toLocaleDateString() : t("Date not recorded")}</time></div>
          {item.url && <a className="offer-link" href={item.url} target="_blank" rel="noreferrer" data-external-link aria-label={`${t("View source")}: ${group.source.name}, ${item.title}`}>{t("View source")}<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><path d="M14 5h5v5M19 5 9 15M19 13v6H5V5h6" /></svg></a>}
        </div>)}</div>
      </div>)}
    </section>)}
  </section>;
}
