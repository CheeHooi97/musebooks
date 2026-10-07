const configuredAPIBase = (import.meta.env.VITE_API_BASE_URL || ((import.meta.env.MODE === "mobile" || import.meta.env.VITE_APP_TARGET === "mobile") ? "https://musebooks.my" : "")).replace(/\/+$/, "");
export function apiUrl(path) {
    const normalizedPath = path.startsWith("/") ? path : `/${path}`;
    return configuredAPIBase ? `${configuredAPIBase}${normalizedPath}` : normalizedPath;
}
