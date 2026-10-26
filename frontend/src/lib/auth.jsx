import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { authRequest, makeOAuthProof, storeSession } from "./auth-client";
import { apiUrl } from "./api";
import { isMobileApp } from "./platform";
import { navigate } from "./router";

const AuthContext = createContext(null);
const emailKey = "musebooks.auth.pending-email";
const proofKey = "musebooks.auth.google-proof";
function pendingEmail() { try { return sessionStorage.getItem(emailKey) || ""; } catch { return ""; } }

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionError, setSessionError] = useState("");
  const [email, setEmail] = useState(pendingEmail);
  const [oauthError, setOAuthError] = useState("");
  const sessionVersion = useRef(0);
  const rememberEmail = next => { setEmail(next); try { sessionStorage.setItem(emailKey, next); } catch { /* This visit still works. */ } };
  const acceptSession = result => { sessionVersion.current++; storeSession(result); setUser(result.user); setLoading(false); setSessionError(""); rememberEmail(""); };
  const refresh = useCallback(async () => {
    const version = ++sessionVersion.current;
    setLoading(true); setSessionError("");
    try { const result = await authRequest("me"); if (version === sessionVersion.current) setUser(result.user); }
    catch (error) {
      if (version !== sessionVersion.current) return;
      if (error.status === 401) { setUser(null); storeSession(null); }
      else setSessionError("We could not load your account. Please try again.");
    } finally { if (version === sessionVersion.current) setLoading(false); }
  }, []);
  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => {
    if (!isMobileApp) return undefined;
    let stopped = false;
    let listener;
    let completing = false;
    const complete = async raw => {
      const url = new URL(raw);
      if (url.protocol !== "my.musebooks.app:" || url.hostname !== "auth" || url.pathname !== "/callback" || completing) return;
      completing = true;
      try {
        if (url.searchParams.has("oauth_error")) throw new Error("Google sign-in did not complete. Please try again.");
        const saved = JSON.parse(sessionStorage.getItem(proofKey) || "null");
        sessionStorage.removeItem(proofKey);
        if (!saved || Date.now() - saved.createdAt > 10 * 60 * 1000) throw new Error("Google sign-in expired. Please try again.");
        const result = await authRequest("oauth/exchange", { code: url.searchParams.get("exchange_code"), verifier: saved.verifier });
        if (stopped) return;
        acceptSession(result);
        navigate("/account", { replace: true });
      } catch (error) { if (!stopped) { setOAuthError(error.message); navigate("/login", { replace: true }); } }
      finally { completing = false; import("@capacitor/browser").then(({ Browser }) => Browser.close()).catch(() => undefined); }
    };
    import("@capacitor/app").then(async ({ App }) => {
      const handle = await App.addListener("appUrlOpen", ({ url }) => { complete(url).catch(() => undefined); });
      if (stopped) { handle.remove(); return; }
      listener = handle;
      const launch = await App.getLaunchUrl();
      if (launch?.url && !stopped) await complete(launch.url);
    }).catch(() => undefined);
    return () => { stopped = true; listener?.remove(); };
  }, []);
  async function googleLogin() {
    setOAuthError("");
    let url = apiUrl("/v1/auth/oauth/google");
    if (isMobileApp) {
      const proof = await makeOAuthProof();
      sessionStorage.setItem(proofKey, JSON.stringify({ verifier: proof.verifier, createdAt: Date.now() }));
      url += `?${new URLSearchParams({ mobile: "1", challenge: proof.challenge })}`;
      const { Browser } = await import("@capacitor/browser");
      await Browser.open({ url });
    } else window.location.assign(url);
  }
  async function logout() {
    await authRequest("logout", {});
    sessionVersion.current++;
    storeSession(null); setUser(null); navigate("/login", { replace: true });
  }
  return <AuthContext.Provider value={{ user, loading, sessionError, refresh, email, rememberEmail, acceptSession, logout, googleLogin, oauthError }}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
