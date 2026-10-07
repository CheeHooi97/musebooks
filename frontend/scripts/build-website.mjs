import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const apiBaseURL = (process.env.NEXT_PUBLIC_API_BASE_URL || "https://musebooks.my").replace(/\/+$/, "");

let parsedAPIBase;
try {
  parsedAPIBase = new URL(apiBaseURL);
} catch {
  throw new Error("NEXT_PUBLIC_API_BASE_URL must be a valid HTTPS URL.");
}
if (parsedAPIBase.protocol !== "https:") {
  throw new Error("NEXT_PUBLIC_API_BASE_URL must use HTTPS.");
}

const result = spawnSync(process.execPath, ["node_modules/next/dist/bin/next", "build"], {
  cwd: frontendRoot,
  stdio: "inherit",
  env: {
    ...process.env,
    CAPACITOR_BUILD: "1",
    NEXT_PUBLIC_CAPACITOR_BUILD: "0",
    NEXT_PUBLIC_API_BASE_URL: apiBaseURL,
  },
});

if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
