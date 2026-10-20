import test from "node:test";
import assert from "node:assert/strict";
import { marketplaceGroups } from "./marketplace-groups.js";

const offer = (id, title, extra = {}) => ({ id, title, format: "physical", status: "active", ...extra });
test("catalog model aliases find unmatched offers under a model's other recorded name", () => {
  const aliases = [["山岸あや花", "山岸逢花", "Aika Yamagishi"]];
  const result = marketplaceGroups([offer("legacy", "山岸 逢花 写真集")], { query: "山岸あや花", aliases });
  assert.equal(result.length, 1);
  assert.equal(result[0].workSlug, undefined);
  assert.equal(marketplaceGroups([offer("other", "Other model 写真集")], { query: "山岸あや花", aliases }).length, 0);
});
test("one verified publication combines formats while format filters retain separate offers", () => {
  const items = [offer("a", "Book", { catalogMatched: true, workSlug: "book" }), offer("b", "Book", { catalogMatched: true, workSlug: "book", format: "digital" })];
  const result = marketplaceGroups(items);
  assert.equal(result.length, 1);
  assert.equal(result[0].format, "mixed");
  assert.deepEqual(result[0].formats, ["physical", "digital"]);
  assert.deepEqual(result[0].items.map(item => item.id), ["a", "b"]);
  assert.deepEqual(marketplaceGroups(items, { format: "physical" })[0].items.map(item => item.id), ["a"]);
  assert.deepEqual(marketplaceGroups(items, { format: "digital" })[0].items.map(item => item.id), ["b"]);
});
test("unmatched physical and digital titles do not imply a shared publication", () => {
  const result = marketplaceGroups([offer("a", "Book"), offer("b", "Book", { format: "digital" })]);
  assert.equal(result.length, 2);
});
test("model credits find digital offers whose titles omit the model name", () => {
  assert.equal(marketplaceGroups([offer("ebook", "Private holiday", { format: "digital", featuredNames: "鈴木ふみ奈,Fumina Suzuki" })], { query: "鈴木ふみ奈" }).length, 1);
});
test("verified book identity groups different marketplace titles", () => {
  const result = marketplaceGroups([offer("a", "Seller A title", { catalogMatched: true, workSlug: "book", workTitle: "Book" }), offer("b", "Seller B title", { catalogMatched: true, workSlug: "book", workTitle: "Book" })]);
  assert.equal(result.length, 1);
  assert.equal(result[0].items.length, 2);
  assert.equal(result[0].workSlug, "book");
});

test("model search matches marketplace titles with spacing variants", () => {
  const result = marketplaceGroups([
    offer("a", "☆斎藤 恭代『いいんだよ？』写真集未開封品☆"),
  ], { query: "斎藤恭代" });
  assert.equal(result.length, 1);
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
