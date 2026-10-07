import { LANGUAGE_OPTIONS, CURRENCY_OPTIONS, usePreferences } from "../lib/preferences";import { useEffect, useRef, useState } from "react";

function ControlIcon({ name }) {
  return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {name === "sun" ? <><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.4 1.4m11.2 11.2L19 19M5 19l1.4-1.4M17.6 6.4 19 5" /></> : name === "moon" ? <path d="M20.5 14.2A8.4 8.4 0 0 1 9.8 3.5 8.6 8.6 0 1 0 20.5 14.2Z" /> : name === "user" ? <><circle cx="12" cy="8" r="3.5" /><path d="M5 21v-2a7 7 0 0 1 14 0v2" /></> : <path d="m8 10 4 4 4-4" />}
  </svg>;
}

export default function HeaderControls({ theme, setTheme, savedCount, onCollection }) {const { t, language, setLanguage, currency, setCurrency, rateState } = usePreferences();
  const [open, setOpen] = useState(false);
  const root = useRef(null);
  const trigger = useRef(null);
  const firstItem = useRef(null);
  useEffect(() => {
    if (!open) return;
    const dismiss = (event) => {if (!root.current?.contains(event.target)) setOpen(false);};
    const escape = (event) => {if (event.key === "Escape") {setOpen(false);trigger.current?.focus();}};
    document.addEventListener("pointerdown", dismiss);
    document.addEventListener("keydown", escape);
    return () => {document.removeEventListener("pointerdown", dismiss);document.removeEventListener("keydown", escape);};
  }, [open]);
  return <div className="header-actions">
    <button className="appearance-control" type="button" onClick={() => setTheme((value) => value === "light" ? "dark" : "light")} aria-label={t(theme === "light" ? "Switch to dark mode" : "Switch to light mode")}>
      <ControlIcon name={theme === "light" ? "sun" : "moon"} /><span>{theme === "light" ? t("Light") : t("Dark")}</span>
    </button>
    <div className="account-control" ref={root} onBlur={(event) => {if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);}}>
      <button className="account-trigger" type="button" ref={trigger} aria-expanded={open} aria-controls="account-dropdown" onClick={() => setOpen((value) => !value)} onKeyDown={(event) => {
        if (event.key === "ArrowDown") {event.preventDefault();setOpen(true);requestAnimationFrame(() => firstItem.current?.focus());}
      }}><span className="account-avatar"><ControlIcon name="user" /></span><span>{t("Account")}</span><ControlIcon name="chevron" /></button>
      {open && <div className="account-dropdown" id="account-dropdown">
        <div className="account-dropdown__intro"><strong>{t("Your MuseBooks")}</strong><p>{t("Your collection is saved on this device.")}</p></div>
        <button type="button" ref={firstItem} onClick={() => {setOpen(false);onCollection();}}>{t("Saved collection")}<span>{savedCount}</span></button>
        <button type="button" onClick={() => setTheme((value) => value === "light" ? "dark" : "light")}>{t(theme === "light" ? "Switch to dark mode" : "Switch to light mode")}<ControlIcon name={theme === "light" ? "moon" : "sun"} /></button>
        <div className="account-preferences">
          <label><span>{t("Language")}</span><select aria-label={t("Language")} value={language} onChange={event => setLanguage(event.target.value)}>{LANGUAGE_OPTIONS.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>
          <label><span>{t("Currency")}</span><select aria-label={t("Currency")} value={currency} onChange={event => setCurrency(event.target.value)}>{CURRENCY_OPTIONS.map(option => <option key={option.value} value={option.value}>{t(option.label)}</option>)}</select></label>
          {currency !== "original" && <p role="status">{t(rateState === "loading" ? "Loading exchange rates…" : rateState === "error" ? "Conversion unavailable. Original prices shown." : "Converted prices are estimates.")}</p>}
        </div>
        <a href="/privacy-policy">{t("Privacy Policy")}</a>
      </div>}
    </div>
  </div>;
}
