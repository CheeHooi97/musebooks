import { useEffect } from "react";
import { Capacitor } from "@capacitor/core";
import { isMobileApp } from "../lib/platform";

const scriptId = "musebooks-hilltop-popunder";
const scriptURL = "https://surprisedplate.com/cyD.9s6/bP2U5PlxSpWgQ/9dNvz/Umz-M/Twck4INZSb0b3/NHTvMCxZNyzCgJ5O";
const directURL = "https://thoroughgear.com/bp3.Vr0PPb3xp/vabUmcV/J_ZuDN0B3/N/TOMCxVNuzOgT1rLwTzcm1NMHz/Ea3COID/kV";

export function WebsiteAds() {
  useEffect(() => {
    if (isMobileApp || Capacitor.isNativePlatform() || document.getElementById(scriptId)) return;
    const script = document.createElement("script");
    script.id = scriptId;
    script.settings = {};
    script.src = scriptURL;
    script.async = true;
    script.referrerPolicy = "no-referrer-when-downgrade";
    script.onerror = () => script.remove();
    document.body.appendChild(script);
    // The vendor installs document listeners. Keep one initialization across
    // route changes and React StrictMode's effect replay.
  }, []);

  if (isMobileApp || Capacitor.isNativePlatform()) return null;
  return <aside className="sponsored-offer" aria-label="Advertisement">
    <span>Advertisement · Sponsored</span>
    <a href={directURL} target="_blank" rel="sponsored noopener noreferrer">Explore this sponsored offer</a>
  </aside>;
}
