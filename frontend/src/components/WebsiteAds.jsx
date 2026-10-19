import { useEffect } from "react";
import { Capacitor } from "@capacitor/core";
import { isMobileApp } from "../lib/platform";

const scriptId = "musebooks-hilltop-popunder";
const scriptURL = "https://surprisedplate.com/c.DE9K6KbM2Y5/l/SDWXQ/9kNXzEU/zqMFTtcD4xNPSp0F3-NDTqMpxlNUz/g/5a";
const directURL = "https://thoroughgear.com/bP3sVx0.P/3yp/vubOmDVSJ-ZyD/0f3RN/T/M/xxNQz/go1cLjTjcr1/MbzDE/3YODD/k-";

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
