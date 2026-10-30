import test from "node:test";
import assert from "node:assert/strict";
import { bookAnswers, bookFactSummary, longDate, fitDescription, profileFactSummary } from "./book-answers.js";

const source = kind => ({ name: kind === "marketplace" ? "Yahoo! JAPAN Auctions" : "Rakuten Books", kind, photobookFormat: "physical" });
const listing = (status, priceMinor, observedAt, extra = {}) => ({ status, priceMinor, currency: "JPY", observedAt, format: "physical", priceType: "fixed", priceCategory: "marketplace_asking", source: source("marketplace"), ...extra });
const book = {
  originalTitle: "美しい果実",
  englishTitle: "Beautiful Fruit",
  photographer: "Takeo Dec.",
  models: [{ name: "本郷柚巴" }],
  editions: [{
    editionLabel: "First print", format: "physical", publisher: "講談社", releaseDate: "2022-06-29T00:00:00Z", releasePrecision: "day", isbn: "9784065284438",
    listings: [
      listing("active", 1800, "2026-10-10T11:00:00Z"),
      listing("active", 1000, "2026-10-09T11:00:00Z"),
      listing("completed", 1200, "2026-09-01T00:00:00Z"),
      listing("completed", 2500, "2026-10-01T00:00:00Z"),
      listing("completed", 1500, "2026-09-15T00:00:00Z"),
      listing("ended", 900, "2026-08-01T00:00:00Z"),
    ],
  }],
};

test("dates read naturally at each recorded precision", () => {
  assert.equal(longDate("2022-06-29"), "June 29, 2022");
  assert.equal(longDate("2022-06"), "June 2022");
  assert.equal(longDate("2022"), "2022");
  assert.equal(longDate(""), "");
});

test("lead summary names people, photographer, publisher and editions", () => {
  assert.equal(bookFactSummary(book), "美しい果実 (Beautiful Fruit) is a photobook featuring 本郷柚巴, photographed by Takeo Dec., published by 講談社 on June 29, 2022. MuseBooks records 1 edition (physical).");
});

test("answers keep asking prices, completed sales and ended listings apart", () => {
  const answers = Object.fromEntries(bookAnswers(book).map(({ question, answer }) => [question, answer]));
  assert.equal(answers["When was 美しい果実 published?"], "美しい果実 was published on June 29, 2022 by 講談社.");
  assert.equal(answers["Who is featured in 美しい果実?"], "本郷柚巴.");
  assert.equal(answers["What is the ISBN of 美しい果実?"], "ISBN 9784065284438.");
  assert.match(answers["How much does 美しい果実 cost?"], /^The lowest recorded active offer is ¥ 1,000 \(active asking price, First print\) on Yahoo! JAPAN Auctions, observed October 9, 2026\. 2 active offers are recorded in JPY\./);
  assert.equal(answers["What has 美しい果実 sold for?"], "3 confirmed completed sales are recorded in JPY, observed from September 1, 2026 to October 1, 2026, from ¥ 1,200 to ¥ 2,500 (median ¥ 1,500). Sold prices are marketplace evidence for that copy and condition, not a valuation.");
});

test("missing facts are stated as not recorded", () => {
  const bare = { originalTitle: "Untitled", editions: [{ editionLabel: "Digital", format: "digital", listings: [] }] };
  const answers = bookAnswers(bare);
  assert.equal(answers[0].answer, "The publication date is not recorded yet.");
  assert.ok(answers.some(item => item.answer.startsWith("No active offer is recorded for this photobook.")));
  assert.ok(!answers.some(item => item.question.startsWith("What has")), "digital-only records have no sold question");
});

test("profile leads use recorded facts, and drop the split when only a preview is loaded", () => {
  const books = [
    { publicationType: "photobook", models: [{ name: "A" }], editions: [{ publisher: "P", releaseDate: "2020-01-01", releasePrecision: "day" }] },
    { publicationType: "magazine_issue", coverModels: [{ name: "A" }], editions: [{ publisher: "P", releaseDate: "2024-01-01", releasePrecision: "day" }] },
  ];
  assert.equal(profileFactSummary({ name: "A", workCount: 2 }, "models", books), "A is featured in 1 photobook and 1 magazine issue recorded by MuseBooks, dated 2020 to 2024. Publishers include P.");
  assert.equal(profileFactSummary({ name: "A", workCount: 30 }, "models", books), "A is featured in 30 publications recorded by MuseBooks.");
  assert.equal(profileFactSummary({ name: "P", workCount: 2 }, "publishers", books), "MuseBooks records 1 photobook and 1 magazine issue from P, dated 2020 to 2024. Featured people include A.");
});

test("meta descriptions end on a whole sentence when one fits", () => {
  const first = "A".repeat(100) + ".";
  assert.equal(fitDescription(first + " " + "B".repeat(100) + "."), first);
  assert.ok(fitDescription("C".repeat(200)).endsWith("…"));
  assert.equal(fitDescription("C".repeat(200)).length, 160);
});

