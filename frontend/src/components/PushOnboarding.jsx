import { useEffect, useRef, useState } from "react";
import Icon from "./Icon";
import { useAuth } from "../lib/auth";
import { usePreferences } from "../lib/preferences";
import { isStandalone } from "../lib/install";
import { isMobileApp } from "../lib/platform";
import { enablePush, pushEnabled, pushSupport } from "../lib/push";

const SEEN_KEY = "musebooks.push-onboarding.seen.v1";

function hasSeenPrompt() {
  try { return localStorage.getItem(SEEN_KEY) === "1"; }
  catch { return false; }
}

export default function PushOnboarding() {
  const { t, language } = usePreferences();
  const auth = useAuth();
  const dialogRef = useRef(null);
  const completed = useRef(false);
  const [open, setOpen] = useState(false);
  const [support, setSupport] = useState("supported");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isMobileApp || !isStandalone() || auth.loading || completed.current || hasSeenPrompt()) return undefined;
    let current = true;
    const available = pushSupport();
    setSupport(available);
    if (available !== "supported" && available !== "denied") return undefined;

    (async () => {
      if (auth.user && available === "supported" && Notification.permission === "granted") {
        try {
          if (await pushEnabled()) {
            completed.current = true;
            try { localStorage.setItem(SEEN_KEY, "1"); } catch { /* Keep this visit complete. */ }
            return;
          }
        } catch { /* Offer the setup again if the existing subscription cannot be checked. */ }
      }
      if (current) setOpen(true);
    })();
    return () => { current = false; };
  }, [auth.loading, auth.user]);

  useEffect(() => {
    if (!open) return undefined;
    const previousFocus = document.activeElement;
    dialogRef.current?.focus();
    document.body.classList.add("has-sheet");
    const onKeyDown = event => {
      if (event.key === "Escape") finish();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.body.classList.remove("has-sheet");
      document.removeEventListener("keydown", onKeyDown);
      previousFocus?.focus?.();
    };
  }, [open]);

  function finish() {
    completed.current = true;
    try { localStorage.setItem(SEEN_KEY, "1"); } catch { /* Keep this visit complete. */ }
    setOpen(false);
  }

  async function turnOn() {
    setBusy(true);
    setError("");
    try {
      await enablePush(language, { title: t("Notifications are on"), body: t("We'll let you know when new photobooks and magazine issues are added.") });
      finish();
    } catch (failure) {
      if (failure.code === "denied") setSupport("denied");
      else if (failure.status === 401) auth.refresh();
      setError(failure.message);
    } finally { setBusy(false); }
  }

  if (!open) return null;
  return <div className="push-onboarding__backdrop">
    <section className="push-onboarding" role="dialog" aria-modal="true" aria-labelledby="push-onboarding-title" tabIndex={-1} ref={dialogRef}>
      <span className="push-onboarding__icon" aria-hidden="true"><Icon name="bell" size={22} /></span>
      <h2 id="push-onboarding-title">{t("New publication notifications")}</h2>
      {!auth.user
        ? <p>{t("Sign in to get a notification when new photobooks and magazine issues are added.")}</p>
        : support === "denied"
          ? <p>{t("Notifications are blocked for this site. Allow them in your browser's site settings, then try again.")}</p>
          : <p>{t("Get one notification a day when new photobooks and magazine issues are added.")}</p>}
      {error && <p role="alert" className="auth-message auth-message--error">{t(error)}</p>}
      <div className="push-onboarding__actions">
        {!auth.user ? <>
          <a className="button" href="/login">{t("Sign in")}</a>
          <a className="button button--ghost" href="/register">{t("Create account")}</a>
        </> : support === "supported" && <button type="button" className="button" disabled={busy} onClick={turnOn}>{t(busy ? "Please wait…" : "Turn on notifications")}</button>}
        <button type="button" className="button button--ghost" disabled={busy} onClick={finish}>{t("Not now")}</button>
      </div>
    </section>
  </div>;
}
