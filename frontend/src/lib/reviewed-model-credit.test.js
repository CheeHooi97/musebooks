import test from "node:test";
import assert from "node:assert/strict";
import { reviewedCreditChangeFor } from "./reviewed-model-credit.js";

const reviews = [
  { model: "浅野こころ", title: "2025 ミス・マガジン", action: "change", to: "永岡ゆきね", evidence: { url: "https://publisher.example/book" } },
  { model: "浅野こころ", title: "別の写真集", action: "keep", evidence: { url: "https://publisher.example/keep" } },
  { model: "浅野こころ", title: "証拠のない変更", action: "change", to: "別人" },
];

test("reviewed credit changes require an exact model, title, change decision and evidence URL", () => {
  assert.equal(reviewedCreditChangeFor("浅野こころ", "2025 ミス・マガジン", reviews), reviews[0]);
  assert.equal(reviewedCreditChangeFor("別のモデル", "2025 ミス・マガジン", reviews), null);
  assert.equal(reviewedCreditChangeFor("浅野こころ", "ミス・マガジン", reviews), null);
  assert.equal(reviewedCreditChangeFor("浅野こころ", "別の写真集", reviews), null);
  assert.equal(reviewedCreditChangeFor("浅野こころ", "証拠のない変更", reviews), null);
});
