import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { PreferencesProvider } from "./lib/preferences";
import { CollectionProvider } from "./lib/collection";
import { AuthProvider } from "./lib/auth";
import "@fontsource/gloock/400.css";
import "@fontsource/hanken-grotesk/400.css";
import "@fontsource/hanken-grotesk/500.css";
import "@fontsource/hanken-grotesk/600.css";
import "@fontsource/azeret-mono/400.css";
import "@fontsource/azeret-mono/500.css";
import "./styles.css";

createRoot(document.getElementById("root")).render(<React.StrictMode>
  <PreferencesProvider><CollectionProvider><AuthProvider><App /></AuthProvider></CollectionProvider></PreferencesProvider>
</React.StrictMode>);
