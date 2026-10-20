import Icon from "./Icon";
import { usePreferences } from "../lib/preferences";
import { useCollection } from "../lib/collection";
import { showCatalogImages } from "../lib/platform";
import { bookPath, bookPeople, bookTitle, editionFormatLabel } from "../lib/catalog";
import { primaryListing, visibleEditions } from "../lib/price-policy";

export function BookCover({ book, edition, compact = false, loading = "lazy" }) {
  const image = showCatalogImages && (edition?.coverUrl || book.coverUrl);
  // Without an image (native builds, missing covers) a typographic plate stands in.
  return <div className={`cover${image ? " cover--image" : " cover--plate"}${compact ? " cover--compact" : ""}`}>
    {image ? <img src={image} alt={compact ? "" : `${book.originalTitle} cover`} loading={loading} fetchPriority={loading === "eager" ? "high" : "auto"} /> : <>
      <span className="cover__mark" aria-hidden="true">{book.originalTitle.slice(0, 2)}</span>
      <span className="cover__title">{bookTitle(book)}</span>
    </>}
  </div>;
}

export default function BookCard({ book, filters = {}, loading = "lazy", showPrice = true }) {
  const { t, formatPrice } = usePreferences();
  const { isSaved, toggleSaved } = useCollection();
  const edition = visibleEditions(book, filters)[0] || book.editions?.[0];
  const listing = primaryListing(edition, filters.availability);
  const people = bookPeople(book).map(person => person.name).filter(Boolean).slice(0, 2).join(" · ");
  const saved = isSaved(book.id);
  return <article className="book-card">
    <a className="book-card__link" href={bookPath(book)} aria-label={`${bookTitle(book)}${people ? `, ${people}` : ""}`}>
      <div className="book-card__cover"><BookCover book={book} edition={edition} loading={loading} /></div>
      <div className="book-card__body">
        <p className="eyebrow">{t(book.origin?.name)} · {t(editionFormatLabel(edition, book))}</p>
        <h3>{book.originalTitle}</h3>
        {people && <p className="book-card__people">{people}</p>}
        {showPrice && <p className="book-card__price">{listing ? formatPrice(listing.priceMinor, listing.currency) : <span>{t(edition ? "Price not recorded" : "No edition record")}</span>}</p>}
      </div>
    </a>
    <button className={`book-card__save${saved ? " is-saved" : ""}`} type="button" onClick={() => toggleSaved(book.id)} aria-pressed={saved} aria-label={`${saved ? t("Remove") : t("Save")} ${bookTitle(book)}`}>
      <Icon name="bookmark" size={17} />
    </button>
  </article>;
}

export function BookGridSkeleton({ count = 8 }) {
  const { t } = usePreferences();
  return <div className="book-grid" role="status" aria-label={t("Loading catalog records")}>
    {Array.from({ length: count }, (_, index) => <div className="book-skeleton" key={index}><span /><i /><i /></div>)}
  </div>;
}
