import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "my.musebooks.app",
  appName: "MuseBooks",
  webDir: "dist",
  plugins: {
    SplashScreen: {
      launchAutoHide: true,
      backgroundColor: "#f7f2e8",
    },
  },
};

export default config;
