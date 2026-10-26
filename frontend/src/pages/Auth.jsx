import { useEffect, useRef, useState } from "react";
import SeoHead from "../components/SeoHead";
import { useAuth } from "../lib/auth";
import { authRequest } from "../lib/auth-client";
import { usePreferences } from "../lib/preferences";
import { navigate } from "../lib/router";

const pages = {
  login: ["Welcome back.", "Sign in to your MuseBooks account.", "Sign in"],
  register: ["Join MuseBooks.", "Create an account with Google or your email address.", "Create account"],
  "verify-email": ["Check your inbox.", "Enter the six-digit code from your email to finish creating your account. Codes expire after 10 minutes.", "Verify email"],
  "forgot-password": ["Forgot your password?", "Enter your email and we’ll send you a password reset code.", "Send reset code"],
  "reset-password": ["A fresh start.", "Enter your emailed reset code and choose a new password. Reset codes expire after 15 minutes.", "Reset password"],
};

function GoogleMark() {
  return <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true"><path fill="#4285f4" d="M43.6 24.5c0-1.4-.1-2.8-.4-4.1H24v7.8h11a9.4 9.4 0 0 1-4.1 6.2v5h6.7c3.9-3.6 6-8.8 6-14.9Z"/><path fill="#34a853" d="M24 44c5.5 0 10.1-1.8 13.5-4.9l-6.7-5a12.2 12.2 0 0 1-18.1-6.4H5.8V33A20.4 20.4 0 0 0 24 44Z"/><path fill="#fbbc05" d="M12.7 27.7a12 12 0 0 1 0-7.4v-5.2H5.8a20 20 0 0 0 0 17.8Z"/><path fill="#ea4335" d="M24 12c3 0 5.7 1 7.8 3l5.9-5.9A19.7 19.7 0 0 0 24 4 20.4 20.4 0 0 0 5.8 15.1l6.9 5.2A12 12 0 0 1 24 12Z"/></svg>;
}

export default function AuthPage({ mode = "login" }) {
  const { t } = usePreferences();
  const auth = useAuth();
  const [email, setEmail] = useState(auth.email || auth.user?.email || "");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [visible, setVisible] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const [providers, setProviders] = useState(null);
  const [providerError, setProviderError] = useState(false);
  const [providerAttempt, setProviderAttempt] = useState(0);
  const errorRef = useRef(null);
  const [title, intro, submitLabel] = pages[mode];
  const social = mode === "login" || mode === "register";
  const password = social || mode === "reset-password";
  const code = mode === "verify-email" || mode === "reset-password";
  useEffect(() => {
    const controller = new AbortController();
    setProviderError(false);
    authRequest("providers", undefined, { signal: controller.signal }).then(setProviders).catch(err => { if (err.name !== "AbortError") setProviderError(true); });
    return () => controller.abort();
  }, [providerAttempt]);
  useEffect(() => { if (error) errorRef.current?.focus(); }, [error]);
  useEffect(() => {
    if (!cooldown) return undefined;
    const timer = setTimeout(() => setCooldown(value => Math.max(0, value - 1)), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);
  useEffect(() => {
    if (auth.user && mode !== "forgot-password" && mode !== "reset-password") {
      navigate("/account", { replace: true });
    }
  }, [auth.user, mode]);
  const oauthCode = new URLSearchParams(window.location.search).get("oauth_error");
  const oauthMessage = auth.oauthError || (oauthCode ? (oauthCode === "oauth_unavailable" ? "Google sign-in is currently unavailable. Please use email or try again later." : "Google sign-in did not complete. Please try again.") : "");

  async function submit(event) {
    event.preventDefault();
    if (busy) return;
    const form = new FormData(event.currentTarget);
    const input = Object.fromEntries(form);
    if (password && new TextEncoder().encode(input.password).length > 72) { setError("Password must be 72 bytes or fewer."); return; }
    if (mode === "register" && input.password !== input.confirmPassword) { setError("Your passwords do not match."); return; }
    delete input.confirmPassword;
    setBusy(true); setError(""); setNotice("");
    try {
      const result = await authRequest(mode, input);
      if (mode === "register") {
        auth.rememberEmail(result.email);
        try { sessionStorage.setItem("musebooks.auth.email-sent", result.sent ? "yes" : "no"); } catch { /* Verification can be resent. */ }
        navigate("/verify-email");
      } else if (mode === "forgot-password") {
        auth.rememberEmail(input.email);
        navigate("/reset-password");
      } else { auth.acceptSession(result); navigate("/account", { replace: true }); }
    } catch (err) {
      if (err.code === "email_not_verified") { auth.rememberEmail(input.email); navigate("/verify-email"); }
      else setError(err.message);
    } finally { setBusy(false); }
  }

  async function resend() {
    if (busy || cooldown) return;
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setError("Enter a valid email address first."); return; }
    setBusy(true); setError(""); setNotice("");
    try {
      await authRequest(mode === "verify-email" ? "resend-verification" : "forgot-password", { email });
      setNotice("If this address needs a code, we’ve sent one. Check your inbox and spam folder."); setCooldown(60);
    } catch (err) { setError(err.message); if (err.status === 429) setCooldown(60); }
    finally { setBusy(false); }
  }

  async function google() {
    setError(""); setBusy(true);
    try { await auth.googleLogin(); } catch { setError("Google sign-in could not open. Please try again."); }
    finally { setBusy(false); }
  }
  let sent = "";
  try { sent = sessionStorage.getItem("musebooks.auth.email-sent"); } catch { /* Optional delivery hint. */ }
  return <div className="page-width auth-page">
    <SeoHead path={`/${mode}`} />
    <section className="auth-panel" aria-labelledby="auth-title">
      <a className="text-link auth-back" href="/books">{t("Back to the catalog")}</a>
      <h1 id="auth-title">{t(title)}</h1>
      <p className="auth-intro">{t(intro)}</p>
      {(error || oauthMessage) && <p className="auth-message auth-message--error" role="alert" tabIndex={-1} ref={errorRef}>{t(error || oauthMessage)}</p>}
      {notice && <p className="auth-message" role="status">{t(notice)}</p>}
      {mode === "verify-email" && sent === "no" && <p className="auth-message" role="status">{t("Your account was created, but the email could not be sent. Request a new code below.")}</p>}
      {mode === "reset-password" && <p className="auth-message">{t("If an account exists for this email, a reset code has been sent. Check your inbox and spam folder.")}</p>}
      {social && <>
        <button className="button button--ghost button--block auth-google" type="button" disabled={busy || !providers?.google} onClick={google}><GoogleMark />{t("Continue with Google")}</button>
        {providers && !providers.google && <p className="auth-hint">{t("Google sign-in is currently unavailable.")}</p>}
        <div className="auth-divider"><span>{t("or with email")}</span></div>
      </>}
      {providerError && <p className="auth-message" role="status">{t("We could not check sign-in availability.")} <button className="text-link" type="button" onClick={() => setProviderAttempt(value => value + 1)}>{t("Try again")}</button></p>}
      {providers?.email === false && mode !== "login" && <p className="auth-message" role="status">{t("Email verification is temporarily unavailable. Please try again later.")}</p>}
      <form className="auth-form" onSubmit={submit} aria-busy={busy}>
        <label htmlFor="auth-email">{t("Email address")}<input id="auth-email" name="email" type="email" autoComplete="email" inputMode="email" required maxLength={254} value={email} onChange={event => setEmail(event.target.value)} autoCapitalize="none" spellCheck="false" /></label>
        {code && <div className="auth-field"><label htmlFor="auth-code">{t("Verification code")}</label><input className="auth-code" id="auth-code" name="code" type="text" inputMode="numeric" pattern="[0-9]{6}" minLength={6} maxLength={6} autoComplete="one-time-code" required aria-describedby="auth-code-help" /><span id="auth-code-help" className="auth-hint">{t("Enter the six-digit code from your email.")}</span></div>}
        {password && <div className="auth-field"><label htmlFor="auth-password">{t(mode === "reset-password" ? "New password" : "Password")}</label>
          <span className="auth-password"><input id="auth-password" name="password" type={visible ? "text" : "password"} autoComplete={mode === "login" ? "current-password" : "new-password"} minLength={mode === "login" ? undefined : 8} required aria-describedby={mode === "login" ? undefined : "auth-password-help"} /><button type="button" onClick={() => setVisible(value => !value)} aria-controls="auth-password" aria-pressed={visible}>{t(visible ? "Hide" : "Show")}</button></span>
          {mode !== "login" && <span id="auth-password-help" className="auth-hint">{t("Use at least 8 characters, up to 72 bytes.")}</span>}
        </div>}
        {mode === "register" && <label htmlFor="auth-confirm">{t("Confirm password")}<input id="auth-confirm" name="confirmPassword" type={visible ? "text" : "password"} autoComplete="new-password" minLength={8} required /></label>}
        {mode === "login" && <a className="text-link auth-forgot" href="/forgot-password">{t("Forgot password?")}</a>}
        <button className="button button--block" type="submit" disabled={busy || (providers?.email === false && mode !== "login")}>{t(busy ? "Please wait…" : submitLabel)}</button>
      </form>
      {code && <button className="text-link auth-resend" type="button" disabled={busy || cooldown > 0 || providers?.email === false} onClick={resend}>{t(cooldown ? "Wait before requesting another code" : "Send a new code")}{cooldown > 0 && ` (${cooldown}s)`}</button>}
      {mode === "register" && <p className="auth-hint auth-verification-note">{t("We’ll email you a verification code. Verify your address before signing in with a password.")}</p>}
      <p className="auth-switch">{t(mode === "register" ? "Already have an account?" : mode === "login" ? "New to MuseBooks?" : "Back to sign in?")} <a className="text-link" href={mode === "login" ? "/register" : "/login"}>{t(mode === "login" ? "Create account" : "Sign in")}</a></p>
      <p className="auth-privacy"><a className="text-link" href="/privacy-policy">{t("Privacy Policy")}</a></p>
    </section>
  </div>;
}

export function AccountPage() {
  const auth = useAuth();
  const { t } = usePreferences();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { if (!auth.loading && !auth.user && !auth.sessionError) navigate("/login", { replace: true }); }, [auth.loading, auth.user, auth.sessionError]);
  async function logout() { setBusy(true); setError(""); try { await auth.logout(); } catch { setError("We could not sign you out. Please try again."); } finally { setBusy(false); } }
  return <div className="page-width auth-page"><SeoHead path="/account" /><section className="auth-panel" aria-labelledby="account-title">
    <h1 id="account-title">{t("Your account")}</h1>
    {auth.loading ? <p role="status">{t("Loading your account…")}</p> : auth.sessionError ? <><p role="alert">{t(auth.sessionError)}</p><button className="button" onClick={auth.refresh}>{t("Try again")}</button></> : auth.user && <>
      <dl className="auth-account"><div><dt>{t("Email address")}</dt><dd>{auth.user.email}</dd></div><div><dt>{t("Email status")}</dt><dd className="auth-verified">{t("Verified")}</dd></div></dl>
      <p className="auth-intro">{t("Your collection and preferences are saved on this device.")}</p>
      <a className="button button--block" href="/saved">{t("View saved collection")}</a>
      <a className="text-link" href="/forgot-password">{t("Reset password")}</a>
      {error && <p role="alert" className="auth-message auth-message--error">{t(error)}</p>}
      <button className="button button--ghost button--block" disabled={busy} onClick={logout}>{t(busy ? "Please wait…" : "Sign out")}</button>
    </>}
  </section></div>;
}
