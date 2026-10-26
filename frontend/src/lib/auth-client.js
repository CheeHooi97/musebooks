import { apiUrl } from "./api.js";
import { isMobileApp } from "./platform.js";

const nativeSessionKey = "musebooks.auth.session.v1";
export function nativeToken() {
  if (!isMobileApp) return "";
  try {
    const session = JSON.parse(localStorage.getItem(nativeSessionKey) || "null");
    if (session?.sessionToken && Date.parse(session.expiresAt) > Date.now()) return session.sessionToken;
    localStorage.removeItem(nativeSessionKey);
  } catch { /* An unavailable store leaves this session in memory. */ }
  return "";
}

let memoryToken = nativeToken();
export function storeSession(result) {
  if (!isMobileApp) return;
  memoryToken = result?.sessionToken || "";
  try {
    if (memoryToken) localStorage.setItem(nativeSessionKey, JSON.stringify({ sessionToken: memoryToken, expiresAt: result.expiresAt }));
    else localStorage.removeItem(nativeSessionKey);
  } catch { /* In-memory sign-in remains available for this app visit. */ }
}

export async function authRequest(path, data, { signal } = {}) {
  const headers = { Accept: "application/json", ...(data === undefined ? {} : { "Content-Type": "application/json" }) };
  if (isMobileApp && memoryToken) headers.Authorization = `Bearer ${memoryToken}`;
  const response = await fetch(apiUrl(`/v1/${isMobileApp ? "mobile/" : ""}auth/${path}`), {
    method: data === undefined ? "GET" : "POST", headers, credentials: isMobileApp ? "omit" : "include",
    ...(data === undefined ? {} : { body: JSON.stringify(data) }), signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(20000)]) : AbortSignal.timeout(20000),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.error) {
    const error = new Error(payload.errmsg || "We could not connect. Please try again.");
    error.status = response.status;
    error.code = payload.code;
    throw error;
  }
  return payload.result;
}

export async function makeOAuthProof() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  const encode = value => btoa(String.fromCharCode(...value)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  const verifier = encode(bytes);
  const challenge = encode(new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier))));
  return { verifier, challenge };
}
