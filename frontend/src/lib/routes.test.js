import { test } from "node:test";
import assert from "node:assert/strict";
import { bookSlugFromPath } from "./routes.js";

test("static server trailing slash preserves book identity", () => {
  assert.equal(bookSlugFromPath("/books/work-taka"), "work-taka");
  assert.equal(bookSlugFromPath("/books/work-taka/"), "work-taka");
  assert.equal(bookSlugFromPath("/books/%E5%AF%AB%E7%9C%9F/"), "寫真");
  assert.equal(bookSlugFromPath("/publishers/press/"), "");
  assert.equal(bookSlugFromPath("/books/%broken/"), "invalid-book");
});
