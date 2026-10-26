import { LANGUAGE_OPTIONS, CURRENCY_OPTIONS, usePreferences } from "../lib/preferences";
import { useCollection } from "../lib/collection";
import { useEffect, useRef, useState } from "react";
import Icon from "./Icon";
import { useAuth } from "../lib/auth";

export default function HeaderControls() {
  const { t, language, setLanguage, currency, setCurrency, rateState } = usePreferences();
  const { saved, theme, toggleTheme } = useCollection();
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const root = useRef(null);
  const trigger = useRef(null);
  const firstItem = useRef(null);
  useEffect(() => {
    if (!open) return undefined;
    const dismiss = event => { if (!root.current?.contains(event.target)) setOpen(false); };
    const escape = event => { if (event.key === "Escape") { setOpen(false); trigger.current?.focus(); } };
    document.addEventListener("pointerdown", dismiss);
    document.addEventListener("keydown", escape);
    return () => { document.removeEventListener("pointerdown", dismiss); document.removeEventListener("keydown", escape); };
  }, [open]);
  return <div className="header-actions">
    <a className="icon-button header-saved" href="/saved" aria-label={`${t("Saved collection")}, ${saved.length}`}>
      <Icon name="bookmark" size={19} />{saved.length > 0 && <span className="badge">{saved.length}</span>}
    </a>
    <button className="icon-button" type="button" onClick={toggleTheme} aria-label={t(theme === "light" ? "Switch to dark mode" : "Switch to light mode")}>
      <Icon name={theme === "light" ? "moon" : "sun"} size={19} />
    </button>
    <div className="menu" ref={root} onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false); }}>
      <button className="icon-button" type="button" ref={trigger} aria-expanded={open} aria-controls="settings-menu" aria-label={t("Account")} onClick={() => setOpen(value => !value)} onKeyDown={event => {
        if (event.key === "ArrowDown") { event.preventDefault(); setOpen(true); requestAnimationFrame(() => firstItem.current?.focus()); }
      }}><Icon name="person" size={19} /></button>
      {open && <div className="menu__panel" id="settings-menu">
        <div className="menu__intro"><strong>{t("Your MuseBooks")}</strong><p>{t("Your collection is saved on this device.")}</p></div>
        <a href={user ? "/account" : "/login"} onClick={() => setOpen(false)}>{t(user ? "Your account" : "Sign in")}</a>
        {!user && <a href="/register" onClick={() => setOpen(false)}>{t("Create account")}</a>}
        <a href="/saved" ref={firstItem} onClick={() => setOpen(false)}>{t("Saved collection")}<span>{saved.length}</span></a>
        <div className="menu__prefs">
          <label><span>{t("Language")}</span><select value={language} onChange={event => setLanguage(event.target.value)}>{LANGUAGE_OPTIONS.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
          <label><span>{t("Currency")}</span><select value={currency} onChange={event => setCurrency(event.target.value)}>{CURRENCY_OPTIONS.map(option => <option key={option.value} value={option.value}>{t(option.label)}</option>)}</select></label>
          {currency !== "original" && <p role="status">{t(rateState === "loading" ? "Loading exchange rates…" : rateState === "error" ? "Conversion unavailable. Original prices shown." : "Converted prices are estimates.")}</p>}
        </div>
        <a href="/about" onClick={() => setOpen(false)}>{t("About MuseBooks")}</a>
        <a href="/privacy-policy" onClick={() => setOpen(false)}>{t("Privacy Policy")}</a>
      </div>}
    </div>
  </div>;
}
