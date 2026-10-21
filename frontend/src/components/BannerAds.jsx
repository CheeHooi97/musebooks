import { useEffect, useRef, useState } from "react";
import { Capacitor } from "@capacitor/core";
import { isMobileApp } from "../lib/platform";

function BannerAd() {
  const frame = useRef(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const receive = (event) => {
      if (event.source === frame.current?.contentWindow && event.data?.type === "musebooks:banner-error") setFailed(true);
    };
    window.addEventListener("message", receive);
    return () => window.removeEventListener("message", receive);
  }, []);
  return <aside className="website-banner" data-failed={failed || undefined} aria-label="Banner advertisement">
    <span>Advertisement</span>
    {failed ? <a href="https://thoroughgear.com/bp3.Vr0PPb3xp/vabUmcV/J_ZuDN0B3/N/TOMCxVNuzOgT1rLwTzcm1NMHz/Ea3COID/kV" target="_blank" rel="sponsored noopener noreferrer">Explore this sponsored offer</a> :
      <iframe ref={frame} title="Banner advertisement" src="/hilltop-banner.html" width="300" height="250" loading="lazy"
        onError={() => setFailed(true)}
        sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox" referrerPolicy="no-referrer-when-downgrade" />}
  </aside>;
}

export function BannerAds() {
  const container = useRef(null);
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!container.current) return;
    const update = () => {
      const width = container.current.getBoundingClientRect().width;
      setCount(width < 300 ? 0 : width >= 624 ? 2 : 1);
    };
    update();
    const observer = new ResizeObserver(update);
    observer.observe(container.current);
    return () => observer.disconnect();
  }, []);
  if (isMobileApp || Capacitor.isNativePlatform()) return null;
  return <div ref={container} className="website-banner-group" data-banner-count={count}>
    {count > 0 && <BannerAd />}
    {count === 2 && <BannerAd />}
  </div>;
}
