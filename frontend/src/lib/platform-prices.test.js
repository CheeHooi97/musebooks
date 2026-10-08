import { test } from "node:test";
import assert from "node:assert/strict";
import { platformGroups } from "./platform-prices.js";
import { editionListings } from "./price-policy.js";

test("platform grouping keeps each seller offer and native currency", () => {
  const source = { id: "store", name: "Store" };
  const offers = [{ id: "a", source, priceMinor: 2400, currency: "JPY" }, { id: "b", source, priceMinor: 1900, currency: "USD" }, { id: "c", source: { id: "other", name: "Other" } }];
  const groups = platformGroups(offers);
  assert.equal(groups.length, 2);
  assert.deepEqual(groups.find(group => group.source.id === "store").items, offers.slice(0, 2));
  assert.equal(offers[2].priceMinor, undefined);
});

test("edition comparison excludes incompatible formats and digital sales", () => {
  const physical = { id: "market", name: "Market", kind: "marketplace", photobookFormat: "physical" };
  const digital = { id: "ebook", name: "Ebook", kind: "digital_store", photobookFormat: "digital" };
  const listings = [{ id: "paper", format: "physical", source: physical, status: "active", priceType: "fixed" }, { id: "ebook", format: "digital", source: digital, status: "active", priceType: "digital", priceCategory: "digital_retail" }, { id: "invalid", format: "digital", source: digital, status: "completed", priceType: "digital" }];
  assert.deepEqual(editionListings({ format: "physical", listings }).map(item => item.id), ["paper"]);
  assert.deepEqual(editionListings({ format: "digital", listings }).map(item => item.id), ["ebook"]);
});
