import SeoHead from "../components/SeoHead";
import { PageHeader } from "../components/Page";
import { usePreferences } from "../lib/preferences";
const privacyContact = "musecards67@gmail.com";
const sections = [
    ["data-we-handle", "Information the service handles"],
    ["device-storage", "Saved collection and settings"],
    ["website-analytics", "Website analytics"],
    ["sharing", "Sharing and external links"],
    ["use-and-disclosure", "How information is used"],
    ["retention", "Retention and deletion"],
    ["security", "Security"],
    ["contact", "Contact"],
    ["changes", "Changes to this policy"],
];
// Places a link at {token} inside a translated sentence so each language keeps its own word order.
const withToken = (text, token, node) => { const [before, after = ""] = text.split(token); return <>{before}{node}{after}</>; };
export default function PrivacyPolicyPage() {
    const { t } = usePreferences();
    const contactLink = <a href={`mailto:${privacyContact}`}>{privacyContact}</a>;
    return (<div className="page-width">
      <SeoHead path="/privacy-policy" />
      <PageHeader eyebrow={t("Legal")} title={t("Privacy Policy")} intro={t("This policy explains how MuseBooks handles information when you use the MuseBooks website and Android app.")}>
        <p className="eyebrow">{t("Last updated October 23, 2026")}</p>
      </PageHeader>

        <div className="article-layout">
          <aside className="article-toc" aria-label={t("Policy contents")}>
            <h2>{t("Contents")}</h2>
            <nav>
              {sections.map(([id, label]) => <a key={id} href={`#${id}`}>{t(label)}</a>)}
            </nav>
          </aside>

          <article className="article">
            <section id="data-we-handle">
              <h2>{t("Information the service handles")}</h2>
              <p>{t("When you browse the catalog, your browser or app requests catalog and origin information from the MuseBooks API and cover images from our image host. Those requests necessarily expose network details such as your IP address, the requested page or resource, and browser or app information to the systems delivering the response. Hosting and delivery providers may process limited technical logs to operate, secure, and troubleshoot the service.")}</p>
              <p>{t("MuseBooks offers Google sign-in and email/password accounts. We store your email address, verification status, a password hash for password accounts, and your Google account identifier and profile image when you use Google. Password accounts must verify their email address. Resend delivers verification and password reset emails. We use this information to authenticate you and protect your account.")}</p>
              <p>{t("Website sign-in uses an HttpOnly session cookie. The app stores a session token on your device. Sessions expire after 30 days and are revoked when you sign out; resetting your password revokes your other sessions. Your collection and preferences remain on your device. Account pages do not load website advertising.")}</p>
            </section>

            <section id="device-storage">
              <h2>{t("Saved collection and settings")}</h2>
              <p>{t("Your saved book list, interface language, display currency, and light or dark appearance setting are stored in browser storage on the device you use. They stay on that device and are not synced to a MuseBooks account or uploaded to our catalog API. When you select a display currency, your browser or app requests exchange rates from Frankfurter. These requests contain currency codes, not your saved collection. Converted prices are estimates. Select Original currency to view the source amounts.")}</p>
            </section>

            <section id="website-analytics">
              <h2>{t("Website analytics")}</h2>
              <p>{t("The MuseBooks website uses Google Analytics to measure visits and understand how visitors use the catalog. The Google tag sends page and browser information to Google and may use cookies to distinguish visits. Your saved collection and appearance setting are not sent as custom analytics data. The Google tag is excluded from the Android and iOS app builds.")}</p>
              <p>{withToken(t("Learn more about how Google handles this information in {link}."), "{link}", <a href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">{t("Google’s Privacy Policy")}</a>)}</p>
            </section>

            <section id="website-advertising">
              <h2>{t("Website advertising")}</h2>
              <p>{t("The website displays sponsored links and loads a third-party HilltopAds script that may open advertising tabs or windows when you interact with the page. Ad providers and destinations receive technical information such as your IP address and browser information and may use cookies or similar technologies under their own privacy policies. These website ads are excluded from the Android and iOS app builds.")}</p>
            </section>

            <section id="sharing">
              <h2>{t("Sharing and external links")}</h2>
              <p>{t("If you choose to share a book, MuseBooks passes that book’s title and link to your device’s share interface. The app you select receives the information you choose to share and handles it under its own privacy policy.")}</p>
              <p>{t("Catalog source links open external retailer or publisher websites. Those sites are operated by others and have their own privacy practices; review their policies before sharing information with them.")}</p>
            </section>

            <section id="use-and-disclosure">
              <h2>{t("How information is used")}</h2>
              <p>{t("MuseBooks uses catalog requests to return books, editions, origins, listings, and cover images. Limited technical request information may be used to keep the service reliable and secure. Website advertising providers process information as described in the Website advertising section above. Your saved collection and settings are not sent to ad providers as custom data.")}</p>
            </section>

            <section id="retention">
              <h2>{t("Retention and deletion")}</h2>
              <p>{t("Your saved books and appearance setting remain in local browser or app storage until you remove them, clear that storage, or remove the app. MuseBooks does not keep server-side copies of those preferences. Technical logs generated by hosting or delivery providers follow their operational retention practices and are kept only as needed for service operation, security, troubleshooting, or legal obligations.")}</p>
              <p>{withToken(t("For a privacy question or a request about information associated with your use of MuseBooks, contact us at {email}."), "{email}", contactLink)}</p>
            </section>

            <section id="security">
              <h2>{t("Security")}</h2>
              <p>{t("The Android app is configured to connect to the production MuseBooks API over HTTPS. We use reasonable safeguards for the service, but no method of transmission or storage can be guaranteed to be completely secure.")}</p>
            </section>

            <section id="contact">
              <h2>{t("Contact")}</h2>
              <p>{withToken(t("For privacy questions or data requests, email {email}. Please identify MuseBooks in your message so we can route your request."), "{email}", contactLink)}</p>
            </section>

            <section id="changes">
              <h2>{t("Changes to this policy")}</h2>
              <p>{t("We may update this policy when the service or its data practices change. The date at the top of this page shows when it was most recently revised.")}</p>
            </section>
          </article>
        </div>
    </div>);
}
