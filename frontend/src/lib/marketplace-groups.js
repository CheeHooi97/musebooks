// A catalog match is authoritative. Resale titles alone are only provisional
// groups; preserve punctuation, edition wording, and bundle descriptions.
export const normalizeSearch = value => String(value || "").normalize("NFKC").toLocaleLowerCase().replace(/\s+/gu, "");

/**
 * Builds a name → aliases lookup from lists of equivalent names, e.g. a
 * MuseBooks model's display, original and English names.
 */
export function aliasIndex(nameLists = []) {
  const index = new Map();
  for (const names of nameLists) {
    const normalized = names.map(normalizeSearch).filter(Boolean);
    for (const name of normalized) {
      const aliases = index.get(name) || new Set();
      normalized.forEach(alias => aliases.add(alias));
      index.set(name, aliases);
    }
  }
  return index;
}

export function marketplaceGroups(items, { query = "", format = "", availability = "", aliases } = {}) {
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
  const index = aliases instanceof Map ? aliases : aliasIndex(aliases);
  const needles = [...(index.get(needle) || [needle])];
  return [...groups.values()].filter(group => {
    if (!needle) return true;
    const haystack = normalizeSearch([group.title, ...group.items.flatMap(item => [item.title, item.featuredNames])].join(" "));
    return needles.some(name => haystack.includes(name));
  });
}
