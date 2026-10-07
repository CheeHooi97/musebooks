export default function BookDetail({ selectedBook, selectedEdition, selectedEditions, selectedListing, availability, saved, shareState, setSelectedEditionId, toggleSaved, shareSelected, BookCover, EditionPrices, Icon, primaryListing, formatPrice, priceLabel, editionFormatLabel }) {
    return <article className="book-detail-page" aria-labelledby="book-title">
      <nav className="book-breadcrumb" aria-label="Breadcrumb"><a href="/">Browse the collection</a><span aria-hidden="true">/</span><span>{selectedBook.originalTitle}</span></nav>
        <section id="editions" className="detail-panel" aria-label="Selected photobook">
          <div className="detail-media">
            <BookCover book={selectedBook} edition={selectedEdition} loading="eager"/>
            <div className="detail-thumbs">
              {selectedBook.editions.map((item) => <button key={item.id} type="button" className={item.id === selectedEdition.id ? "thumb--selected" : ""} onClick={() => setSelectedEditionId(item.id)} aria-label={`View ${item.editionLabel}`} aria-pressed={item.id === selectedEdition.id}><BookCover book={selectedBook} edition={item} compact/></button>)}
              {selectedBook.editions.length > 1 && <a className="more-thumb" href="#available-editions">All editions</a>}
            </div>
          </div>
          <div className="detail-copy">
            <h1 id="book-title" tabIndex={-1}>{selectedBook.originalTitle}</h1>
            {selectedBook.englishTitle && <p className="detail-title">{selectedBook.englishTitle}</p>}
            {selectedBook.summary && <p className="book-summary">{selectedBook.summary}</p>}
            <div className="detail-facts">
              <span><b>Photographer</b>{selectedBook.photographer || "Not recorded"}</span>
              <span><b>Origin</b>{selectedBook.origin.name}</span>
              <span><b>Format</b>{editionFormatLabel(selectedEdition.format)}</span>
              <span><b>Language</b>{selectedEdition.language || "Not recorded"}</span>
              <span><b>Pages</b>{selectedEdition.pageCount ? `${selectedEdition.pageCount} pages` : "Not recorded"}</span>
              <span><b>Published</b>{selectedEdition.releaseDate ? new Date(selectedEdition.releaseDate).getFullYear() : "Not recorded"}</span>
              <span><b>Publisher</b>{selectedEdition.publisher || "Not recorded"}</span>
              <span><b>Market</b>{selectedEdition.editionMarket || "Not recorded"}</span>
            </div>
            <div className="edition-heading" id="available-editions"><h3>Available editions</h3><a href="#edition-list">View all</a></div>
            <div className="edition-list" id="edition-list">
              {selectedEditions.map((item) => {
                    const itemListing = primaryListing(item);
                    const active = item.id === selectedEdition.id;
                    return <div className={`edition-row${active ? " edition-row--active" : ""}`} key={item.id}>
                  <button className="edition-row__select" type="button" onClick={() => setSelectedEditionId(item.id)} aria-pressed={active}>
                    <strong>{item.editionLabel}</strong><span>{editionFormatLabel(item.format)} · {priceLabel(item, itemListing)}</span>
                  </button>
                  <strong>{itemListing ? formatPrice(itemListing.priceMinor, itemListing.currency) : "No price"}</strong>
                  {itemListing?.url ? <a href={itemListing.url} target="_blank" rel="noreferrer" data-external-link>View source</a> : <span className="quiet-state">No source</span>}
                </div>;
                })}
            </div>
            <EditionPrices edition={selectedEdition}/>
            <div className="detail-actions">
              {selectedListing && <a className="action-primary" href={selectedListing.url} target="_blank" rel="noreferrer" data-external-link><Icon name="external" size={16}/> Visit source site</a>}
              <button type="button" onClick={() => toggleSaved(selectedBook.id)} aria-pressed={saved.includes(selectedBook.id)}><Icon name="bookmark" size={16}/> {saved.includes(selectedBook.id) ? "Saved to collection" : "Save to collection"}</button>
              <button type="button" onClick={shareSelected}><Icon name="share" size={16}/> {shareState === "shared" ? "Share sheet opened" : shareState === "copied" ? "Link copied" : "Share"}</button>
            </div>
          </div>
        </section>
    </article>;
}
