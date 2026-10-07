import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { formatPrice as sourcePrice } from "./price-policy";
import messages from "./translations.json";

export const LANGUAGE_OPTIONS = [{ value: "en", label: "English" }, { value: "ja", label: "日本語" }, { value: "zh-Hans", label: "简体中文" }, { value: "zh-Hant", label: "繁體中文" }];
export const CURRENCY_OPTIONS = [{ value: "original", label: "Original currency" }, { value: "JPY", label: "JPY ¥" }, { value: "MYR", label: "MYR RM" }, { value: "USD", label: "USD $" }, { value: "TWD", label: "TWD NT$" }, { value: "HKD", label: "HKD HK$" }, { value: "SGD", label: "SGD S$" }, { value: "CNY", label: "CNY CN¥" }];
const KEY = "musebooks.account.preferences.v1";
const locales = { en: "en-US", ja: "ja-JP", "zh-Hans": "zh-CN", "zh-Hant": "zh-TW" };
function readPreferences() {
  try { const value = JSON.parse(localStorage.getItem(KEY) || "{}"); return { language: LANGUAGE_OPTIONS.some(option => option.value === value.language) ? value.language : "en", currency: CURRENCY_OPTIONS.some(option => option.value === value.currency) ? value.currency : "original" }; }
  catch { return { language: "en", currency: "original" }; }
}
export function translate(value, language) {
  if (typeof value !== "string" || language === "en") return value;
  const text = value.replace(/\s+/g, " ").trim();
  const direct = messages[language]?.[text];
  if (direct) return direct;
  const count = text.match(/^(\d+) (saved books?|books?|catalog entr(?:y|ies)|listings?)$/);
  if (count) { const nouns = { ja: ["保存済みの本", "冊", "件のカタログ項目", "件の出品"], "zh-Hans": ["本已收藏", "本书", "个目录条目", "条记录"], "zh-Hant": ["本已收藏", "本書", "個目錄項目", "筆紀錄"] }; return `${count[1]} ${nouns[language][count[2].startsWith("saved") ? 0 : count[2].startsWith("book") ? 1 : count[2].startsWith("catalog") ? 2 : 3]}`; }
  return value;
}
const Preferences = createContext(null);
export function PreferencesProvider({ children }) {
  const [preferences, setPreferences] = useState(readPreferences);
  const [rates, setRates] = useState(null);
  const [rateState, setRateState] = useState("idle");
  const { language, currency } = preferences;
  useEffect(() => {
    document.documentElement.lang = language;
    try { localStorage.setItem(KEY, JSON.stringify(preferences)); } catch { /* Preferences still work for this visit. */ }
  }, [preferences, language]);
  useEffect(() => {
    const sync = event => { if (event.key === KEY) setPreferences(readPreferences()); };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);
  useEffect(() => {
    if (currency === "original" || rates) return;
    const controller = new AbortController();
    setRateState("loading");
    fetch("https://api.frankfurter.dev/v2/rates?base=USD&quotes=JPY,MYR,TWD,HKD,SGD,CNY,KRW,EUR,GBP", { signal: controller.signal })
      .then(response => { if (!response.ok) throw new Error("Rates unavailable"); return response.json(); })
      .then(rows => {
        const values = { USD: 1 };
        for (const row of rows) if (Number.isFinite(row.rate) && row.rate > 0) values[row.quote.toUpperCase()] = row.rate;
        if (Object.keys(values).length < 2) throw new Error("Rates unavailable");
        if (!controller.signal.aborted) { setRates(values); setRateState("ready"); }
      }).catch(() => { if (!controller.signal.aborted) setRateState("error"); });
    return () => controller.abort();
  }, [currency, rates]);
  const value = useMemo(() => ({
    language, currency, rateState,
    setLanguage: next => { if (LANGUAGE_OPTIONS.some(option => option.value === next)) setPreferences(current => ({ ...current, language: next })); },
    setCurrency: next => { if (CURRENCY_OPTIONS.some(option => option.value === next)) setPreferences(current => ({ ...current, currency: next })); },
    t: text => translate(text, language),
    formatPrice: (minor, source) => {
      if (minor === undefined || !source) return translate("Price on site", language);
      const original = sourcePrice(minor, source);
      if (currency === "original" || source === currency || !rates?.[source] || !rates?.[currency]) return original;
      const amount = minor / (["JPY", "KRW"].includes(source) ? 1 : 100);
      const converted = amount / rates[source] * rates[currency];
      return new Intl.NumberFormat(locales[language], { style: "currency", currency }).format(converted);
    },
  }), [language, currency, rates, rateState]);
  return <Preferences.Provider value={value}>{children}</Preferences.Provider>;
}
export function usePreferences() { return useContext(Preferences); }
