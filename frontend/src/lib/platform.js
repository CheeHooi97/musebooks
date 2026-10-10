// Native bundles are image-free; website images remain available at every viewport.
export const isMobileApp = import.meta.env.MODE === "mobile" || import.meta.env.VITE_APP_TARGET === "mobile";
export const showCatalogImages = !isMobileApp;
