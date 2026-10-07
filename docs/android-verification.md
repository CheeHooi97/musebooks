# Android verification

Inspected and fixed on 7 October 2026.

- Android contained stale Next.js web assets and generated webDir=out configuration. Synced the verified Vite mobile-mode bundle and current webDir=dist configuration with Capacitor.
- Verified packaged entry assets exist, no Next.js entry remains, and the bundle uses the HTTPS MuseBooks API.
- Fixed INTERNET permission placement before application in AndroidManifest.xml.
- Built the final debug APK successfully using Android Studio's JDK 21 and installed SDK 36.
- Android app lint completed successfully. Remaining warnings concern dependency/tooling version updates; no app lint errors remain. Capacitor's own lint baseline suppresses upstream issues.
- Public GET /v1/models returned HTTP 200, 289 total records, and Access-Control-Allow-Origin=https://localhost for Android WebView requests.
- The detected emulator was offline; reconnecting did not yield an online device, and no usable local AVD profile was found. On-device navigation, hardware back, browser/share plugins, and installation were not verified.

Debug APK: frontend/android/app/build/outputs/apk/debug/app-debug.apk

For future changes, run npm run cap:sync from frontend before building Android. That command builds in mobile mode before copying assets. Do not use a plain website build as the native bundle.
