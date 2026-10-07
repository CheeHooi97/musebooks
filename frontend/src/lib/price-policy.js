// Keep each format's store prices separate from physical marketplace history.
export function editionListings(edition) {
    return edition.listings.filter((listing) => {
        const marketplace = ["marketplace", "marketplace_c2c", "auction", "flea_market"].includes(listing.source.kind);
        const store = ["bookstore", "digital_store"].includes(listing.source.kind);
        const sourceFormat = listing.source.photobookFormat || (marketplace ? "physical" : store ? "digital" : undefined);
        const listingFormat = listing.format || (listing.priceType === "digital" ? "digital" : marketplace ? "physical" : undefined);
        if (sourceFormat !== edition.format || listingFormat !== edition.format)
            return false;
        if (edition.format === "digital") {
            return listing.status !== "completed" && (!listing.priceType || listing.priceType === "digital") &&
                (!listing.priceCategory || listing.priceCategory === "digital_retail");
        }
        return listing.priceType !== "digital" && listing.priceCategory !== "digital_retail";
    });
}
export function visibleEditions(book, filters) {
    return book.editions.filter((edition) => (!filters.format || edition.format === filters.format) &&
        (!filters.language || edition.language?.includes(filters.language)) &&
        (!filters.availability || editionListings(edition).some((listing) => listing.status === filters.availability)));
}
export function primaryListing(edition, status = "") {
    if (!edition)
        return undefined;
    const listings = editionListings(edition);
    if (status)
        return listings.find((listing) => listing.status === status);
    return listings.find((listing) => listing.status === "active") ||
        listings.find((listing) => listing.status === "unknown") ||
        listings.find((listing) => listing.status === "completed") || listings[0];
}
export function priceLabel(edition, listing) {
    if (!listing)
        return edition.format === "digital" ? "No retail price recorded" : "No marketplace price recorded";
    if (edition.format === "digital")
        return listing.status === "ended" ? "Last retail price" : "Digital retail price";
    if (listing.priceCategory === "physical_retail")
        return listing.status === "ended" ? "Last physical retail price" : "Physical retail price";
    if (listing.status === "completed")
        return "Sold price";
    return listing.status === "active" ? "Active asking price" : "Last asking price";
}
export function formatPrice(priceMinor, currency) {
    if (priceMinor === undefined || !currency)
        return "Price on site";
    const digits = currency === "JPY" || currency === "KRW" ? 0 : 2;
    const amount = priceMinor / (digits ? 100 : 1);
    const symbols = { JPY: "¥", TWD: "NT$", CNY: "CN¥", MYR: "RM", USD: "US$" };
    return (symbols[currency] || currency) + " " + amount.toLocaleString("en-US", { maximumFractionDigits: digits });
}
