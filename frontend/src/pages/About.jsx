import SeoHead from "../components/SeoHead";
import { PageHeader } from "../components/Page";
import { ABOUT_SECTIONS } from "../lib/about";
import { usePreferences } from "../lib/preferences";

const slug = title => title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export default function About() {
  const { t } = usePreferences();
  return <div className="page-width">
    <SeoHead path="/about" />
    <PageHeader eyebrow={t("About")} title={t("About MuseBooks")} intro={t("How the catalog records each work, edition and source-backed price — and how to send a correction.")} />
    <div className="article-layout">
      <aside className="article-toc" aria-label={t("Contents")}><h2>{t("Contents")}</h2><nav>{ABOUT_SECTIONS.map(([title]) => <a key={title} href={`#${slug(title)}`}>{t(title)}</a>)}</nav></aside>
      <article className="article">
        {ABOUT_SECTIONS.map(([title, text]) => <section key={title} id={slug(title)}><h2>{t(title)}</h2><p>{t(text)}</p></section>)}
        <section id="corrections"><h2>{t("Corrections")}</h2><p>{t("Spotted a wrong credit, edition or price?")} <a href="mailto:musecards67@gmail.com">{t("Send a catalog correction")}</a>.</p></section>
      </article>
    </div>
  </div>;
}
