import { useEffect } from "react";
import { pageSeo } from "../lib/seo";
import { languageAlternates } from "../lib/catalog-languages";

export default function SeoHead({ path, book, profile, noindex = false, pending = false }) {
  useEffect(() => {
    if (pending) return;
    const seo = pageSeo(path, book, profile);
    document.title = seo.title;
    const set = (attribute, key, content) => {
      let element = document.head.querySelector(`meta[${attribute}="${key}"]`);
      if (!content) { element?.remove(); return; }
      if (!element) { element = document.createElement("meta"); element.setAttribute(attribute, key); document.head.appendChild(element); }
      element.content = content;
    };
    set("name", "description", seo.description);
    set("name", "robots", noindex || seo.noindex ? "noindex,follow" : "index,follow,max-image-preview:large");
    for (const [key, value] of Object.entries({ title: seo.title, description: seo.description, url: seo.url, type: "website", site_name: "MuseBooks", image: seo.image })) set("property", `og:${key}`, value);
    for (const [key, value] of Object.entries({ title: seo.title, description: seo.description, card: seo.image ? "summary_large_image" : "summary", image: seo.image })) set("name", `twitter:${key}`, value);
    let canonical = document.head.querySelector('link[rel="canonical"]');
    if (!canonical) { canonical = document.createElement("link"); canonical.rel = "canonical"; document.head.appendChild(canonical); }
    canonical.href = seo.url;
    document.head.querySelectorAll('link[hreflang]').forEach(element => element.remove());
    if (!noindex && !seo.noindex) for (const item of languageAlternates(path, new URL(seo.url).origin)) {
      const alternate = document.createElement("link");
      alternate.rel = "alternate"; alternate.hreflang = item.code; alternate.href = item.url;
      document.head.appendChild(alternate);
    }
    let json = document.getElementById("musebooks-seo-jsonld");
    if (!json) { json = document.createElement("script"); json.id = "musebooks-seo-jsonld"; json.type = "application/ld+json"; document.head.appendChild(json); }
    json.textContent = JSON.stringify(seo.structuredData);
  }, [path, book, profile, noindex, pending]);
  return null;
}
