import { readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { marketplaceGroups } from "../src/lib/marketplace-groups.js";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "../..");
const readJson = async file => JSON.parse(await readFile(file, "utf8"));
const queue = await readJson(path.join(root, "scraper/japan-models/queue.json"));
const exclusions = await readJson(path.join(root, "scraper/japan-models/excluded-listings.json"));
const checkpoint = await readJson(path.join(root, "scraper/japan-models/import-checkpoint.json"));
const verification = await readJson(path.join(root, "scraper/japan-models/import-verification.json"));
const excludedKeys = new Set(exclusions.map(item => `${item.sourceId}\0${item.externalId}`));
const expectedByModel = new Map();
const excludedByModel = new Map();
const allItems = new Map();
const workNames = new Map();
const invalidPaidOffers = [];
let importedModelAssociations = 0;
let pendingAssociations = 0;

const stableJson = value => {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(", ")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}: ${stableJson(value[key])}`).join(", ")}}`;
  }
  return JSON.stringify(value);
};

for (const row of queue) {
  const modelDir = path.resolve(root, row.directory);
  const model = (await readJson(path.join(modelDir, "model.json"))).models[0];
  const importPath = row.status === "reuse_fumina_capture"
    ? path.join(root, "scraper/fumina-suzuki-expanded/home-import.json")
    : path.join(modelDir, "home-import.json");
  const records = await readJson(importPath);
  const modelKey = String(model.id);
  expectedByModel.set(modelKey, new Map());
  excludedByModel.set(modelKey, 0);

  for (const record of records) {
    const digest = createHash("sha256").update(stableJson(record)).digest("hex");
    const recordImported = row.status === "reuse_fumina_capture" || (record.batch.items || []).every(offer => {
      const importKey = `${modelKey}:${record.source.id}:${offer.externalId}`;
      return checkpoint.records[importKey] === digest;
    });
    const workId = record.work?.id || "";
    if (recordImported && workId) {
      const names = workNames.get(workId) || new Set();
      for (const name of (record.work.featuredNames || "").split(",")) {
        if (name.trim()) names.add(name.trim());
      }
      workNames.set(workId, names);
    }

    for (const offer of record.batch.items || []) {
      const key = `${record.source.id}\0${offer.externalId}`;
      if (!recordImported) {
        pendingAssociations++;
        continue;
      }
      importedModelAssociations++;
      if (excludedKeys.has(key)) {
        excludedByModel.set(modelKey, excludedByModel.get(modelKey) + 1);
        continue;
      }
      expectedByModel.get(modelKey).set(key, offer.format);
      if (!Number.isInteger(offer.priceMinor) || offer.priceMinor <= 0 || !offer.currency) {
        invalidPaidOffers.push({ modelId: modelKey, sourceId: record.source.id, externalId: offer.externalId, issue: "missing_or_nonpositive_price" });
      }
      if (!offer.imageUrl) {
        invalidPaidOffers.push({ modelId: modelKey, sourceId: record.source.id, externalId: offer.externalId, issue: "missing_cover" });
      }

      const previous = allItems.get(key);
      if (previous && previous.format !== offer.format) {
        throw new Error(`Conflicting formats for ${record.source.id}/${offer.externalId}`);
      }
      const merged = previous || {
        id: key,
        title: offer.title,
        format: offer.format,
        status: offer.status,
        priceMinor: offer.priceMinor,
        currency: offer.currency,
        imageUrl: offer.imageUrl || "",
        featuredNames: "",
        catalogMatched: false,
      };
      if (workId) {
        merged.workId = workId;
        merged.workSlug = record.work.slug || workId;
        merged.workTitle = record.work.originalTitle || offer.title;
        merged.catalogMatched = true;
      }
      allItems.set(key, merged);
    }
  }
}

// Fumina's pilot contains one Rakuma listing that was imported before the
// reusable home-import manifest was assembled. Include that preserved row in
// the model search/filter check so the homepage total matches the database.
const fuminaRow = queue.find(row => row.status === "reuse_fumina_capture");
if (fuminaRow) {
  const fuminaCapture = await readJson(path.join(root, "scraper/fumina-suzuki-expanded/listings.json"));
  const modelKey = String(fuminaRow.musecardsPersonId);
  for (const offer of fuminaCapture.items || []) {
    if (offer.importStatus !== "already_imported") continue;
    const key = `${offer.sourceId}\0${offer.externalId}`;
    if (expectedByModel.get(modelKey).has(key)) continue;

    expectedByModel.get(modelKey).set(key, offer.format);
    importedModelAssociations++;
    const item = allItems.get(key) || {
      id: key,
      title: offer.title,
      format: offer.format,
      status: offer.status,
      priceMinor: offer.priceMinor,
      currency: offer.currency,
      imageUrl: offer.imageUrl || "",
      featuredNames: "",
      catalogMatched: false,
    };
    item.featuredNames = [...new Set([...(item.featuredNames || "").split(","), fuminaRow.name].filter(Boolean))].join(",");
    allItems.set(key, item);
    if (!Number.isInteger(offer.priceMinor) || offer.priceMinor <= 0 || !offer.currency) {
      invalidPaidOffers.push({ modelId: modelKey, sourceId: offer.sourceId, externalId: offer.externalId, issue: "missing_or_nonpositive_price" });
    }
    if (!offer.imageUrl) {
      invalidPaidOffers.push({ modelId: modelKey, sourceId: offer.sourceId, externalId: offer.externalId, issue: "missing_cover" });
    }
  }
}

for (const item of allItems.values()) {
  item.featuredNames = [...(workNames.get(item.workId) || [])].join(",");
}

const importedItems = [...allItems.values()];
const liveMode = process.argv.includes("--live");
let liveApi = null;
let items = importedItems;
const catalogIdentityIssues = [];
if (liveMode) {
  const apiBase = (process.env.MUSEBOOKS_PUBLIC_API_BASE || "https://musebooks.my").replace(/\/+$/, "");
  const pageSize = 50;
  const loadPage = async page => {
    const response = await fetch(`${apiBase}/v1/marketplace-listings?region=JP&scope=offers&status=all&pageSize=${pageSize}&page=${page}`);
    if (!response.ok) throw new Error(`Marketplace API page ${page} returned HTTP ${response.status}`);
    return response.json();
  };
  const firstPage = await loadPage(1);
  const records = [...(firstPage.items || [])];
  for (let start = 2; start <= firstPage.totalPages; start += 4) {
    const pages = await Promise.all(Array.from(
      { length: Math.min(4, firstPage.totalPages - start + 1) },
      (_, index) => loadPage(start + index),
    ));
    records.push(...pages.flatMap(page => page.items || []));
  }
  const byIdentity = new Map();
  for (const item of records) {
    if (!item.source?.id || !item.externalId) throw new Error("Marketplace API returned an offer without source identity");
    const key = `${item.source.id}\0${item.externalId}`;
    byIdentity.set(key, { ...item, id: key });
  }
  if (records.length !== firstPage.total) {
    throw new Error(`Marketplace API returned ${records.length} rows; page one reported ${firstPage.total}`);
  }
  for (const expected of importedItems) {
    if (!expected.catalogMatched || !expected.workSlug) continue;
    const actual = byIdentity.get(expected.id);
    if (!actual?.catalogMatched || actual.workSlug !== expected.workSlug) {
      catalogIdentityIssues.push({ offer: expected.id, expectedWork: expected.workSlug,
        actualWork: actual?.workSlug || null });
    }
  }
  liveApi = {
    base: apiBase,
    total: firstPage.total,
    totalPages: firstPage.totalPages,
    received: records.length,
    uniqueOffers: byIdentity.size,
    duplicateRows: records.length - byIdentity.size,
  };
  items = [...byIdentity.values()];
}
const allGroups = marketplaceGroups(items);
const marketplaceGroupingIssues = [];
const groupedWorks = new Set();
for (const group of allGroups) {
  if (!group.workSlug) continue;
  if (groupedWorks.has(group.workSlug)) marketplaceGroupingIssues.push({ workSlug: group.workSlug, issue: "publication_split_across_cards" });
  groupedWorks.add(group.workSlug);
}
const crossFormatReview = await readJson(path.join(root, "scraper/japan-cross-format-identities.json"));
const reviewedCrossFormatGroups = crossFormatReview.pairs.map(pair => {
  const groups = allGroups.filter(group => group.workSlug === pair.physicalWorkId);
  const offers = groups.flatMap(group => group.items);
  const physicalOffers = offers.filter(item => item.format === "physical").length;
  const digitalOffers = offers.filter(item => item.format === "digital").length;
  return { workSlug: pair.physicalWorkId, title: pair.title, cards: groups.length,
    physicalOffers, digitalOffers, passed: groups.length === 1 && physicalOffers > 0 && digitalOffers > 0 };
});
const results = [];
for (const row of queue) {
  const modelId = String(row.musecardsPersonId);
  const query = row.name;
  const expected = expectedByModel.get(modelId) || new Map();
  const visible = new Set(marketplaceGroups(items, { query }).flatMap(group => group.items.map(item => item.id)));
  const physical = new Set(marketplaceGroups(items, { query, format: "physical" }).flatMap(group => group.items.map(item => item.id)));
  const digital = new Set(marketplaceGroups(items, { query, format: "digital" }).flatMap(group => group.items.map(item => item.id)));
  const physicalExpected = [...expected].filter(([, format]) => format === "physical");
  const digitalExpected = [...expected].filter(([, format]) => format === "digital");
  const visibleCount = [...expected.keys()].filter(key => visible.has(key)).length;
  const physicalVisible = physicalExpected.filter(([key]) => physical.has(key)).length;
  const digitalVisible = digitalExpected.filter(([key]) => digital.has(key)).length;

  results.push({
    modelId: row.musecardsPersonId,
    name: row.name,
    counts: {
      all: expected.size,
      physical: physicalExpected.length,
      digital: digitalExpected.length,
      excludedFreePreviews: excludedByModel.get(modelId) || 0,
      searchable: visibleCount,
      physicalFilter: physicalVisible,
      digitalFilter: digitalVisible,
    },
    filtersPassed: visibleCount === expected.size &&
      physicalVisible === physicalExpected.length && digitalVisible === digitalExpected.length,
  });
}

const result = {
  checkedAt: new Date().toISOString(),
  mode: liveMode ? "live_public_api_and_frontend_marketplace_filters" : "imported_manifest_and_frontend_marketplace_filters",
  liveApi,
  databaseVerification: verification.result,
  importedModelAssociations,
  pendingAssociations,
  importedMarketplaceItems: importedItems.length,
  searchedMarketplaceItems: items.length,
  excludedListings: exclusions.length,
  invalidPaidOffers,
  catalogIdentityIssues,
  marketplaceGroupingIssues,
  reviewedCrossFormatGroups,
  results,
};
const output = path.join(root, "scraper/japan-models/homepage-models-verification.json");
await writeFile(output, `${JSON.stringify(result, null, 2)}\n`, "utf8");
const failures = results.filter(row => !row.filtersPassed);
console.log(liveMode
  ? `Verified homepage search and format filters for ${results.length} Japanese models against ${items.length} live marketplace offers; failures=${failures.length}; paid-offer metadata issues=${invalidPaidOffers.length}`
  : `Verified homepage search and format filters for ${results.length} Japanese models; ${items.length} unique imported offers; failures=${failures.length}; paid-offer metadata issues=${invalidPaidOffers.length}`);
console.log(`Catalog work identity issues=${catalogIdentityIssues.length}`);
console.log(`Publication grouping issues=${marketplaceGroupingIssues.length}; reviewed physical/digital groups passed=${reviewedCrossFormatGroups.filter(group => group.passed).length}/${reviewedCrossFormatGroups.length}`);
if (failures.length || invalidPaidOffers.length || catalogIdentityIssues.length || marketplaceGroupingIssues.length || reviewedCrossFormatGroups.some(group => !group.passed)) process.exitCode = 1;
