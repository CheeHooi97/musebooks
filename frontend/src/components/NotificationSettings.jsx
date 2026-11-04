import { useEffect, useState } from "react";
import Icon from "./Icon";
import { useAuth } from "../lib/auth";
import { usePreferences } from "../lib/preferences";
import { disablePush, enablePush, pushEnabled, pushSupport } from "../lib/push";

// Daily notification when new publications are added. As with MuseCards
// alerts, it needs an account: signed-out visitors are asked to sign in or
// create one first.
export default function NotificationSettings({ id = "notifications" }) {
  const { t, language } = usePreferences();
  const auth = useAuth();
  const [support, setSupport] = useState(() => pushSupport());
  const [state, setState] = useState("loading"); // loading | on | off
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const signedIn = Boolean(auth.user);

  useEffect(() => {
    if (!signedIn || support !== "supported") return undefined;
    let current = true;
    pushEnabled().then(on => { if (current) setState(on ? "on" : "off"); }).catch(() => { if (current) setState("off"); });
    return () => { current = false; };
  }, [signedIn, support]);

  async function turnOn() {
    setBusy(true); setError("");
    try {
      await enablePush(language, { title: t("Notifications are on"), body: t("We'll let you know when new photobooks and magazine issues are added.") });
      setState("on");
    } catch (failure) {
      if (failure.code === "denied") setSupport("denied");
      else if (failure.status === 401) auth.refresh();
      setError(failure.message);
    } finally { setBusy(false); }
  }
  async function turnOff() {
    setBusy(true); setError("");
    try { await disablePush(); setState("off"); }
    catch (failure) { setError(failure.message); }
    finally { setBusy(false); }
  }

  let body;
  if (auth.loading) body = null;
  else if (!signedIn) body = <>
    <p>{t("Sign in to get a notification when new photobooks and magazine issues are added.")}</p>
    <div className="notify-card__actions"><a className="button" href="/login">{t("Sign in")}</a><a className="button button--ghost" href="/register">{t("Create account")}</a></div>
  </>;
  else if (support === "ios-install") body = <p>{t("On iPhone and iPad, add MuseBooks to your Home Screen first: tap Share, then Add to Home Screen. Open it from there to turn on notifications.")}</p>;
  else if (support === "denied") body = <p>{t("Notifications are blocked for this site. Allow them in your browser's site settings, then try again.")}</p>;
  else if (support !== "supported") body = <p>{t("This browser can't show notifications.")}</p>;
  else body = <>
    <p>{t(state === "on" ? "On for this device. You'll get one notification a day when new publications are added." : "Get one notification a day when new photobooks and magazine issues are added.")}</p>
    <div className="notify-card__actions">
      {state === "on"
        ? <button type="button" className="button button--ghost" disabled={busy} onClick={turnOff}>{t(busy ? "Please wait…" : "Turn off")}</button>
        : <button type="button" className="button" disabled={busy || state === "loading"} onClick={turnOn}>{t(busy ? "Please wait…" : "Turn on notifications")}</button>}
    </div>
  </>;

  return <section className="notify-card" id={id} aria-labelledby={`${id}-title`}>
    <span className="notify-card__icon" aria-hidden="true"><Icon name="bell" size={20} /></span>
    <div className="notify-card__body">
      <h2 id={`${id}-title`}>{t("New publication notifications")}</h2>
      {body}
      {error && <p role="alert" className="auth-message auth-message--error">{t(error)}</p>}
    </div>
  </section>;
}
