import SeoHead from "../components/SeoHead";
import { ABOUT_SECTIONS } from "../lib/about";
export default function About() {
  return <div className="site-shell privacy-page"><SeoHead path="/about" /><header className="site-header"><a className="wordmark" href="/">MuseBooks</a><nav className="main-nav"><a href="/">Catalog</a><a href="/privacy-policy">Privacy Policy</a></nav></header><main id="main-content"><h1>About MuseBooks</h1>{ABOUT_SECTIONS.map(([title, text]) => <section key={title}><h2>{title}</h2><p>{text}</p></section>)}<p><a href="mailto:musecards67@gmail.com">Send a catalog correction</a></p></main></div>;
}
