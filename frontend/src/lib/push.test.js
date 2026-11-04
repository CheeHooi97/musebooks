import test from "node:test";
import assert from "node:assert/strict";
import { pushSupport, serverKey } from "./push.js";

const browser = ({ permission = "default", push = true, ua = "Mozilla/5.0 (Windows NT 10.0)", standalone = false } = {}) => ({
  navigator: { userAgent: ua, serviceWorker: {}, standalone },
  matchMedia: () => ({ matches: standalone }),
  ...(push ? { PushManager: class {}, Notification: { permission } } : {}),
});

test("notification support covers blocked sites and iPhones outside the Home Screen", () => {
  assert.equal(pushSupport(browser()), "supported");
  assert.equal(pushSupport(browser({ permission: "denied" })), "denied");
  assert.equal(pushSupport(browser({ push: false })), "unsupported");
  assert.equal(pushSupport(browser({ push: false, ua: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)" })), "ios-install");
  assert.equal(pushSupport(undefined), "unsupported");
});

test("the server key decodes from base64url to the 65-byte P-256 point", () => {
  const key = "BAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
  const bytes = serverKey(key);
  assert.equal(bytes.length, 65);
  assert.equal(bytes[0], 4);
  assert.deepEqual([...serverKey("-_8")], [0xfb, 0xff]);
});
