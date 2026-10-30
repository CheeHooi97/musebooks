import SeoHead from "../components/SeoHead";
import { PageHeader } from "../components/Page";
import { usePreferences } from "../lib/preferences";
import { GUIDE_EXAMPLE, GUIDE_UPDATED, guideFor } from "../lib/guides";

export default function Guide({ path }) {
  const { language } = usePreferences();
  const guide = guideFor(path, language);
  return <div className="page-width">
    <SeoHead path={path} />
    <PageHeader eyebrow="MuseBooks" title={guide.title} intro={guide.description} />
    <article className="article">
      {guide.sections.map(([heading, text]) => <section key={heading}><h2>{heading}</h2><p>{text}</p></section>)}
      <p><a className="text-link" href={GUIDE_EXAMPLE}>{guide.example[0]}</a> · <a className="text-link" href="/books">{guide.example[1]}</a></p>
      <p className="results-count"><time dateTime={GUIDE_UPDATED}>{GUIDE_UPDATED}</time></p>
    </article>
  </div>;
}
