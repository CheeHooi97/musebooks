export function bookSlugFromPath(pathname) {
  if (!pathname.startsWith("/books/")) return "";
  try { return decodeURIComponent(pathname.slice(7).replace(/\/+$/, "")); }
  catch { return "invalid-book"; }
}
