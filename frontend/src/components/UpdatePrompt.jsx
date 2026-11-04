import { useState } from "react";
import { usePreferences } from "../lib/preferences";
import { applyUpdate, snoozeUpdate, useUpdateAvailable } from "../lib/sw-updates";

// Pop-up when a new release of the site has downloaded in the background.
export default function UpdatePrompt() {
  const { t } = usePreferences();
  const available = useUpdateAvailable();
  const [updating, setUpdating] = useState(false);
  if (!available) return null;
  return <div className="update-prompt" role="alertdialog" aria-labelledby="update-prompt-title" aria-describedby="update-prompt-text">
    <img className="update-prompt__icon" src="/icon-192.png" alt="" width="40" height="40" />
    <div className="update-prompt__body">
      <p id="update-prompt-title" className="update-prompt__title">{t("A new version of MuseBooks is ready")}</p>
      <p id="update-prompt-text" className="update-prompt__text">{t("Update now to get the latest catalog features and fixes.")}</p>
      <div className="update-prompt__actions">
        <button type="button" className="button" disabled={updating} onClick={() => { setUpdating(true); applyUpdate(); }}>{t(updating ? "Updating…" : "Update")}</button>
        <button type="button" className="button button--ghost" disabled={updating} onClick={snoozeUpdate}>{t("Later")}</button>
      </div>
    </div>
  </div>;
}
