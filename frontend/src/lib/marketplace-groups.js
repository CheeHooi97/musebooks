// A catalog match is authoritative. Resale titles alone are only provisional
// groups; preserve punctuation, edition wording, and bundle descriptions.
import modelSearchAliases from "./model-search-aliases.js";

const normalizeSearch = value => String(value || "").normalize("NFKC").toLocaleLowerCase().replace(/\s+/gu, "");
const aliasesByName = new Map();
for (const names of modelSearchAliases) {
  const normalized = names.map(normalizeSearch).filter(Boolean);
  for (const name of normalized) {
    const aliases = aliasesByName.get(name) || new Set();
    normalized.forEach(alias => aliases.add(alias));
    aliasesByName.set(name, aliases);
  }
}

export function marketplaceGroups(items, { query = "", format = "", availability = "" } = {}) {
  const groups = new Map();
  for (const item of items) {
    if (format && item.format !== format) continue;
    if (availability && item.status !== availability) continue;
    const title = item.title?.normalize("NFKC").trim().replace(/\s+/g, " ") || "";
    const itemFormat = item.format || "physical";
    const identity = item.catalogMatched && item.workSlug ? `work:${item.workSlug}` : title ? `title:${title}` : `listing:${item.id}`;
    const key = item.catalogMatched && item.workSlug ? identity : `${itemFormat}:${identity}`;
    if (!groups.has(key)) groups.set(key, { key, format: itemFormat, formats: [], title: item.workTitle || item.title, workSlug: item.catalogMatched ? item.workSlug : undefined, imageUrl: item.imageUrl, items: [] });
    const group = groups.get(key);
    if (!group.formats.includes(itemFormat)) group.formats.push(itemFormat);
    group.formats.sort((a, b) => (a === "physical" ? 0 : 1) - (b === "physical" ? 0 : 1));
    group.format = group.formats.length > 1 ? "mixed" : itemFormat;
    group.items.push(item);
  }
  const needle = normalizeSearch(query.trim());
  const needles = [...(aliasesByName.get(needle) || [needle])];
  return [...groups.values()].filter(group => {
    if (!needle) return true;
    const haystack = normalizeSearch([group.title, ...group.items.flatMap(item => [item.title, item.featuredNames])].join(" "));
    return needles.some(name => haystack.includes(name));
  });
}
