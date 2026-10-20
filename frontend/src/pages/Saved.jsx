import { useMemo, useState } from "react";
import SeoHead from "../components/SeoHead";
import Icon from "../components/Icon";
import BookCard, { BookGridSkeleton } from "../components/BookCard";
import { LoadState, PageHeader } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { useCollection } from "../lib/collection";
import { loadAllBooks, sortBooks, useLoader } from "../lib/catalog";

export default function Saved() {
  const { t } = usePreferences();
  const { saved } = useCollection();
  const [sortBy, setSortBy] = useState("added");
  const books = useLoader(loadAllBooks, []);
  const items = useMemo(() => {
    if (books.state !== "live") return [];
    const byId = new Map(books.data.map(book => [book.id, book]));
    const list = saved.map(id => byId.get(id)).filter(Boolean);
    return sortBy === "added" ? list.reverse() : sortBooks(list, sortBy);
  }, [books.state, books.data, saved, sortBy]);
  return <div className="page-width">
    <SeoHead path="/saved" noindex />
    <PageHeader eyebrow={t("Your collection")} title={t("Saved collection")} intro={t("Publications you save are kept on this device only — no account, no sync.")}>
      {items.length > 1 && <label className="select-field"><span>{t("Sort by")}</span><select value={sortBy} onChange={event => setSortBy(event.target.value)}>
        <option value="added">{t("Recently saved")}</option><option value="newest">{t("Newest release")}</option><option value="title">{t("Title")}</option>
      </select></label>}
    </PageHeader>
    {saved.length === 0 ? <div className="empty-state"><Icon name="bookmark" size={26} /><h2>{t("Your collection is ready.")}</h2><p>{t("Save a publication to keep its editions and source prices close.")}</p><a className="button" href="/books">{t("Browse the catalog")}</a></div> :
      books.state === "loading" ? <BookGridSkeleton count={Math.min(saved.length, 8)} /> :
      books.state !== "live" ? <LoadState state={books.state} retry={books.retry} errorMessage="The catalog couldn’t be reached." /> :
      <>
        <p className="results-count" role="status">{items.length} {t(items.length === 1 ? "saved publication" : "saved publications")}</p>
        <div className="book-grid">{items.map(book => <BookCard key={book.id} book={book} />)}</div>
      </>}
  </div>;
}
