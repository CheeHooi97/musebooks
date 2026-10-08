export function platformGroups(items) {
  const groups = new Map();
  for (const item of items) {
    const key = item.source.id;
    if (!groups.has(key)) groups.set(key, { source: item.source, items: [] });
    groups.get(key).items.push(item);
  }
  return [...groups.values()].sort((a, b) => a.source.name.localeCompare(b.source.name));
}
