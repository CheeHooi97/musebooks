// A catalog match is authoritative. Resale titles alone are only provisional
// groups; preserve punctuation, edition wording, and bundle descriptions.
export function marketplaceGroups(items, { query = "", format = "", availability = "" } = {}) {
  const groups = new Map();
  for (const item of items) {
    if (format && item.format !== format) continue;
    if (availability && item.status !== availability) continue;
    const title = item.title?.normalize("NFKC").trim().replace(/\s+/g, " ") || "";
    const key = item.catalogMatched && item.workSlug ? `work:${item.workSlug}` : title ? `title:${title}` : `listing:${item.id}`;
    if (!groups.has(key)) groups.set(key, { key, title: item.workTitle || item.title, workSlug: item.catalogMatched ? item.workSlug : undefined, imageUrl: item.imageUrl, items: [] });
    groups.get(key).items.push(item);
  }
  const needle = query.trim().normalize("NFKC").toLocaleLowerCase();
  return [...groups.values()].filter(group => !needle || [group.title, ...group.items.map(item => item.title)].join(" ").normalize("NFKC").toLocaleLowerCase().includes(needle));
}
