import test from "node:test";
import assert from "node:assert/strict";
import { marketplaceGroups } from "./marketplace-groups.js";

const offer = (id, title, extra = {}) => ({ id, title, format: "physical", status: "active", ...extra });
test("verified book identity groups different marketplace titles", () => {
  const result = marketplaceGroups([offer("a", "Seller A title", { catalogMatched: true, workSlug: "book", workTitle: "Book" }), offer("b", "Seller B title", { catalogMatched: true, workSlug: "book", workTitle: "Book" })]);
  assert.equal(result.length, 1);
  assert.equal(result[0].items.length, 2);
  assert.equal(result[0].workSlug, "book");
});
test("unmatched exact titles group, while editions and bundles stay distinct", () => {
  const result = marketplaceGroups([offer("a", "Book  Title"), offer("b", "Book Title"), offer("c", "Book Title signed"), offer("d", "Book Title 5冊セット")]);
  assert.equal(result.length, 3);
  assert.equal(result[0].items.length, 2);
  assert.equal(result[0].workSlug, undefined);
});
test("search retains all offers of a matching group and filters format/status", () => {
  const items = [offer("a", "Seller A", { catalogMatched: true, workSlug: "book", workTitle: "Book" }), offer("b", "Seller B", { catalogMatched: true, workSlug: "book", workTitle: "Book", status: "completed" })];
  assert.equal(marketplaceGroups(items, { query: "Seller B" })[0].items.length, 2);
  assert.equal(marketplaceGroups(items, { availability: "completed" })[0].items.length, 1);
  assert.equal(marketplaceGroups(items, { format: "digital" }).length, 0);
});
