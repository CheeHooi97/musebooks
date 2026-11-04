import test from "node:test";
import assert from "node:assert/strict";
import { installKind, isIOS, recentlyDismissed } from "./install.js";

const base = { standalone: false, ios: false, hasPrompt: false, installed: false, dismissed: false };

test("install banner offers the browser prompt, iOS steps, or nothing", () => {
  assert.equal(installKind({ ...base, hasPrompt: true }), "prompt");
  assert.equal(installKind({ ...base, ios: true }), "ios");
  assert.equal(installKind(base), "", "browsers that cannot install see no banner");
  for (const hidden of ["standalone", "installed", "dismissed"]) assert.equal(installKind({ ...base, hasPrompt: true, ios: true, [hidden]: true }), "", hidden);
});

test("a dismissal hides the banner for 30 days", () => {
  const now = Date.UTC(2026, 10, 4);
  assert.equal(recentlyDismissed(String(now - 29 * 864e5), now), true);
  assert.equal(recentlyDismissed(String(now - 31 * 864e5), now), false);
  for (const value of [null, "", "garbage", "0"]) assert.equal(recentlyDismissed(value, now), false);
});

test("iPhone, iPad and iPadOS desktop mode count as iOS", () => {
  assert.equal(isIOS({ userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" }), true);
  assert.equal(isIOS({ userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", platform: "MacIntel", maxTouchPoints: 5 }), true);
  assert.equal(isIOS({ userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", platform: "MacIntel", maxTouchPoints: 0 }), false);
  assert.equal(isIOS({ userAgent: "Mozilla/5.0 (Linux; Android 15)" }), false);
});
