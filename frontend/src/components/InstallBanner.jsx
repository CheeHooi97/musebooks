import { useState } from "react";
import Icon from "./Icon";
import { usePreferences } from "../lib/preferences";
import { dismissInstall, promptInstall, useInstallBanner } from "../lib/install";

// Top-of-page offer to install the web app. Chromium opens the browser's own
// install dialog; iOS gets the Share > Add to Home Screen steps.
export default function InstallBanner() {
  const { t } = usePreferences();
  const { kind, visible } = useInstallBanner();
  const [showSteps, setShowSteps] = useState(false);
  if (!visible) return null;
  const install = () => kind === "prompt" ? promptInstall() : setShowSteps(true);
  return <aside className="install-banner" aria-label={t("Install MuseBooks")}>
    <div className="install-banner__inner">
      <img className="install-banner__icon" src="/icon-192.png" alt="" width="36" height="36" />
      <p className="install-banner__text" role={showSteps ? "status" : undefined}>
        <strong>{t("Install MuseBooks")}</strong>
        <span>{showSteps ? t("Tap Share, then Add to Home Screen.") : t("Add it to your home screen for quick access and offline reading.")}</span>
      </p>
      {!showSteps && <button type="button" className="button install-banner__action" onClick={install}>{t("Install")}</button>}
      <button type="button" className="icon-button install-banner__close" onClick={dismissInstall} aria-label={t("Not now")}><Icon name="close" size={18} /></button>
    </div>
  </aside>;
}
