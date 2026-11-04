import { readFile, writeFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { aliasIndex, marketplaceGroups, modelsMatchingExactName, normalizeSearch } from "../src/lib/marketplace-groups.js";
import { reviewedCreditChangeFor } from "../src/lib/reviewed-model-credit.js";
// The scraper queue was built from the MuseCards model export; this back-office
// check keeps using it. The website itself only uses MuseBooks catalog names.
import modelSearchAliases from "../src/lib/model-search-aliases.js";
const aliases = aliasIndex(modelSearchAliases);

function matchingOfferIds(groups, query, format) {
  const needle = normalizeSearch(query.trim());
  const needles = [...(aliases.get(needle) || [needle])];
  const matched = new Set();
  for (const group of groups) {
    const visibleItems = group.items.filter(item => !format || item.format === format);
    if (!visibleItems.length) continue;
    const haystack = normalizeSearch([group.title, ...visibleItems.flatMap(item => [item.title, item.featuredNames])].join(" "));
    if (!needle || needles.some(name => haystack.includes(name))) {
      for (const item of visibleItems) matched.add(item.id);
    }
  }
  return matched;
}

async function readJsonResponse(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${url}`);
  return response.json();
}

async function loadExactModelRecords(apiBase, query) {
  const records = [];
  const pageSize = 50;
  let page = 1;
  let totalPages = 1;
  do {
    const params = new URLSearchParams({ q: query, pageSize: String(pageSize), page: String(page) });
    const data = await readJsonResponse(`${apiBase}/v1/models?${params}`);
    records.push(...(data.items || []));
    totalPages = Number(data.totalPages || 1);
    page++;
  } while (page <= totalPages);
  return modelsMatchingExactName(records, query);
}

async function loadExactModelOffers(apiBase, modelIds, format = "", searchQuery = "") {
  const byIdentity = new Map();
  const batches = modelIds.length
    ? Array.from({ length: Math.ceil(modelIds.length / 100) }, (_, index) => modelIds.slice(index * 100, (index + 1) * 100))
    : [[]];
  for (const ids of batches) {
    const seenCursors = new Set();
    let cursor = "";
    do {
      const params = new URLSearchParams({ region: "JP", scope: "offers", status: "all", limit: "50", sort: "observed" });
      if (format) params.set("format", format);
      if (searchQuery) params.set("q", searchQuery);
      for (const id of ids) params.append("model", id);
      if (cursor) params.set("cursor", cursor);
      const data = await readJsonResponse(`${apiBase}/v1/marketplace-listings?${params}`);
      for (const item of data.items || []) {
        if (!item.source?.id || !item.externalId) throw new Error("Model offer response lacks a source identity");
        const id = `${item.source.id}\0${item.externalId}`;
        byIdentity.set(id, { ...item, id });
      }
      const next = data.nextCursor || "";
      if (next && seenCursors.has(next)) throw new Error("Model offer pagination cursor repeated");
      if (next) seenCursors.add(next);
      cursor = next;
    } while (cursor);
  }
  return [...byIdentity.values()];
}

async function mapLimit(rows, limit, callback) {
  const results = new Array(rows.length);
  let next = 0;
  await Promise.all(Array.from({ length: Math.min(limit, rows.length) }, async () => {
    while (next < rows.length) {
      const index = next++;
      results[index] = await callback(rows[index], index);
    }
  }));
  return results;
}

const sameSet = (left, right) => left.size === right.size && [...left].every(value => right.has(value));

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "../..");
const readJson = async file => JSON.parse(await readFile(file, "utf8"));
const queue = await readJson(path.join(root, "scraper/japan-models/queue.json"));
const exclusions = await readJson(path.join(root, "scraper/japan-models/excluded-listings.json"));
const checkpoint = await readJson(path.join(root, "scraper/japan-models/import-checkpoint.json"));
const verification = await readJson(path.join(root, "scraper/japan-models/import-verification.json"));
const creditReviewRows = await readJson(path.join(root, "docs/model-bucket-review-2026-10-20.json")).catch(() => []);
const reviewedCreditAdjustments = new Map();
const identityPlan = await readJson(path.join(root, "scraper/japan-work-identities.json")).catch(() => ({ groups: [] }));
const reviewedWorkByEdition = new Map((identityPlan.groups || []).flatMap(group =>
  (group.members || []).map(member => [member.editionId, group.workId]),
));
const exclusionByKey = new Map(exclusions.map(item => [`${item.sourceId}\0${item.externalId}`, item]));
const excludedKeys = new Set(exclusionByKey.keys());
const expectedByModel = new Map();
const excludedByModel = new Map();
const excludedFreePreviewsByModel = new Map();
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
  const records = await readJson(importPath).catch(error => {
    if (error.code === "ENOENT") return [];
    throw error;
  });
  const fuminaImported = row.status === "reuse_fumina_capture"
    ? new Set((await readJson(path.join(root, "scraper/fumina-suzuki-expanded/listings.json")).catch(() => ({ items: [] })))
      .items.filter(offer => offer.importStatus === "already_imported")
      .map(offer => `${offer.sourceId}\0${offer.externalId}`))
    : new Set();
  const modelKey = String(model.id);
  expectedByModel.set(modelKey, new Map());
  excludedByModel.set(modelKey, 0);
  excludedFreePreviewsByModel.set(modelKey, 0);

  for (const record of records) {
    const digest = createHash("sha256").update(stableJson(record)).digest("hex");
    const recordImported = row.status === "reuse_fumina_capture" || (record.batch.items || []).every(offer => {
      const importKey = `${modelKey}:${record.source.id}:${offer.externalId}`;
      return checkpoint.records[importKey] === digest;
    });
    const workId = reviewedWorkByEdition.get(record.edition?.id) || record.edition?.workId || record.work?.id || "";
    if (recordImported && workId) {
      const names = workNames.get(workId) || new Set();
      const creditChange = reviewedCreditChangeFor(row.name, record.work?.originalTitle, creditReviewRows);
      const removedNames = new Set((creditChange?.from || "").split(",").map(normalizeSearch));
      for (const name of (record.work.featuredNames || "").split(",")) {
        if (name.trim() && !removedNames.has(normalizeSearch(name))) names.add(name.trim());
      }
      if (creditChange) {
        for (const name of names) if (removedNames.has(normalizeSearch(name))) names.delete(name);
        for (const name of (creditChange.to || "").split(",")) if (name.trim()) names.add(name.trim());
      }
      workNames.set(workId, names);
    }

    for (const offer of record.batch.items || []) {
      const key = `${record.source.id}\0${offer.externalId}`;
      if (row.status === "reuse_fumina_capture") {
        if (!fuminaImported.has(key)) pendingAssociations++;
        continue;
      }
      if (!recordImported) {
        pendingAssociations++;
        continue;
      }
      importedModelAssociations++;
      if (excludedKeys.has(key)) {
        excludedByModel.set(modelKey, excludedByModel.get(modelKey) + 1);
        if (exclusionByKey.get(key)?.reason === "free_preview") {
          excludedFreePreviewsByModel.set(modelKey, excludedFreePreviewsByModel.get(modelKey) + 1);
        }
        continue;
      }
      const creditChange = reviewedCreditChangeFor(row.name, record.work?.originalTitle || offer.title, creditReviewRows);
      if (creditChange) {
        reviewedCreditAdjustments.set(`${modelKey}\0${key}`, {
          musecardsPersonIdExternalReference: modelKey,
          modelName: row.name,
          sourceId: record.source.id,
          externalId: offer.externalId,
          title: creditChange.title,
          format: offer.format,
          from: creditChange.from,
          to: creditChange.to,
          reason: creditChange.reason,
          evidenceUrl: creditChange.evidence.url,
        });
        continue;
      }
      expectedByModel.get(modelKey).set(key, offer.format);
      if (!Number.isInteger(offer.priceMinor) || offer.priceMinor <= 0 || !offer.currency) {
        invalidPaidOffers.push({ musecardsPersonIdExternalReference: modelKey, sourceId: record.source.id, externalId: offer.externalId, issue: "missing_or_nonpositive_price" });
      }
      if (!offer.imageUrl) {
        invalidPaidOffers.push({ musecardsPersonIdExternalReference: modelKey, sourceId: record.source.id, externalId: offer.externalId, issue: "missing_cover" });
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
        url: offer.url || "",
        sourceName: record.source.name || "",
        observedAt: offer.observedAt || "",
        imageUrl: offer.imageUrl || "",
        featuredNames: "",
        catalogMatched: false,
      };
      if (workId) {
        merged.workId = workId;
        merged.workSlug = workId;
        merged.workTitle = record.work.originalTitle || offer.title;
        merged.catalogMatched = true;
      }
      merged.url ||= offer.url || "";
      merged.sourceName ||= record.source.name || "";
      merged.observedAt ||= offer.observedAt || "";
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
      invalidPaidOffers.push({ musecardsPersonIdExternalReference: modelKey, sourceId: offer.sourceId, externalId: offer.externalId, issue: "missing_or_nonpositive_price" });
    }
    if (!offer.imageUrl) {
      invalidPaidOffers.push({ musecardsPersonIdExternalReference: modelKey, sourceId: offer.sourceId, externalId: offer.externalId, issue: "missing_cover" });
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
let liveModelFilters = new Map();
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

  const checks = await mapLimit(queue, 4, async row => {
    try {
      const matchedModels = await loadExactModelRecords(apiBase, row.name);
      const modelIds = [...new Set(matchedModels.map(model => model.id).filter(Boolean))];
      const searchMode = modelIds.length ? "model_id" : "text_fallback";
      const [all, physical, digital] = await Promise.all([
        loadExactModelOffers(apiBase, modelIds, "", modelIds.length ? "" : row.name),
        loadExactModelOffers(apiBase, modelIds, "physical", modelIds.length ? "" : row.name),
        loadExactModelOffers(apiBase, modelIds, "digital", modelIds.length ? "" : row.name),
      ]);
      return { modelCount: matchedModels.length, modelIds, searchMode, all, physical, digital, error: "" };
    } catch (error) {
      return { modelCount: 0, modelIds: [], searchMode: "error", all: [], physical: [], digital: [], error: String(error?.message || error) };
    }
  });
  liveModelFilters = new Map(queue.map((row, index) => [String(row.musecardsPersonId), checks[index]]));
}
const itemById = new Map(items.map(item => [item.id, item]));
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
  const liveFilter = liveMode ? liveModelFilters.get(modelId) : null;
  const liveQuery = liveFilter?.searchMode === "model_id" ? "" : query;
  const liveAllGroups = liveFilter ? marketplaceGroups(liveFilter.all, { query: liveQuery }) : [];
  const livePhysicalGroups = liveFilter ? marketplaceGroups(liveFilter.physical, { query: liveQuery, format: "physical" }) : [];
  const liveDigitalGroups = liveFilter ? marketplaceGroups(liveFilter.digital, { query: liveQuery, format: "digital" }) : [];
  const visible = liveMode
    ? new Set(liveAllGroups.flatMap(group => group.items.map(item => item.id)))
    : matchingOfferIds(allGroups, query, "");
  const physical = liveMode
    ? new Set(livePhysicalGroups.flatMap(group => group.items.map(item => item.id)))
    : matchingOfferIds(allGroups, query, "physical");
  const digital = liveMode
    ? new Set(liveDigitalGroups.flatMap(group => group.items.map(item => item.id)))
    : matchingOfferIds(allGroups, query, "digital");
  const physicalExpected = [...expected].filter(([, format]) => format === "physical");
  const digitalExpected = [...expected].filter(([, format]) => format === "digital");
  const visibleCount = [...expected.keys()].filter(key => visible.has(key)).length;
  const physicalVisible = physicalExpected.filter(([key]) => physical.has(key)).length;
  const digitalVisible = digitalExpected.filter(([key]) => digital.has(key)).length;

  const liveExpected = new Map(liveAllGroups.flatMap(group => group.items.map(item => [item.id, item.format])));
  const modelExpected = liveMode ? liveExpected : expected;
  const modelPhysicalExpected = [...modelExpected].filter(([, format]) => format === "physical");
  const modelDigitalExpected = [...modelExpected].filter(([, format]) => format === "digital");
  const modelVisibleCount = [...modelExpected.keys()].filter(key => visible.has(key)).length;
  const modelPhysicalVisible = modelPhysicalExpected.filter(([key]) => physical.has(key)).length;
  const modelDigitalVisible = modelDigitalExpected.filter(([key]) => digital.has(key)).length;
  const liveModelOfferIds = new Set(liveAllGroups.flatMap(group => group.items.map(item => item.id)));
  const livePhysicalOfferIds = new Set(livePhysicalGroups.flatMap(group => group.items.map(item => item.id)));
  const liveDigitalOfferIds = new Set(liveDigitalGroups.flatMap(group => group.items.map(item => item.id)));
  const manifestExpectedSearchable = [...expected.keys()].filter(key => (liveMode ? liveModelOfferIds : visible).has(key)).length;
  const manifestPhysicalSearchable = physicalExpected.filter(([key]) => (liveMode ? livePhysicalOfferIds : physical).has(key)).length;
  const manifestDigitalSearchable = digitalExpected.filter(([key]) => (liveMode ? liveDigitalOfferIds : digital).has(key)).length;
  const expectedPhysicalIds = new Set([...modelExpected].filter(([, format]) => format === "physical").map(([key]) => key));
  const expectedDigitalIds = new Set([...modelExpected].filter(([, format]) => format === "digital").map(([key]) => key));
  const liveFormatFiltersPassed = !liveMode || Boolean(liveFilter && !liveFilter.error &&
    (liveFilter.searchMode === "text_fallback" || liveFilter.modelCount > 0) &&
    sameSet(liveModelOfferIds, new Set(visible)) &&
    sameSet(livePhysicalOfferIds, new Set(physical)) && sameSet(liveDigitalOfferIds, new Set(digital)) &&
    sameSet(expectedPhysicalIds, livePhysicalOfferIds) && sameSet(expectedDigitalIds, liveDigitalOfferIds));
  const manifestCoveragePassed = manifestExpectedSearchable === expected.size &&
    manifestPhysicalSearchable === physicalExpected.length && manifestDigitalSearchable === digitalExpected.length;
  const missingImportedManifestOffers = [...expected.keys()].filter(key => !(liveMode ? liveModelOfferIds : visible).has(key)).map(key => {
    const expectedItem = allItems.get(key) || {};
    const liveItem = itemById.get(key) || {};
      const [sourceId, externalId] = key.split("\0");
      return {
        sourceId,
        sourceName: expectedItem.sourceName || liveItem.source?.name || "",
        externalId,
        title: expectedItem.title || liveItem.title || "",
        format: expected.get(key),
        url: expectedItem.url || liveItem.url || "",
        observedAt: expectedItem.observedAt || liveItem.observedAt || "",
        priceMinor: expectedItem.priceMinor ?? liveItem.priceMinor ?? null,
        currency: expectedItem.currency || liveItem.currency || "",
        status: expectedItem.status || liveItem.status || "unknown",
        expectedCredits: expectedItem.featuredNames || "",
      liveCredits: Array.isArray(liveItem.featuredNames) ? liveItem.featuredNames.join(",") : liveItem.featuredNames || "",
      liveWorkSlug: liveItem.workSlug || "",
    };
  });

  results.push({
    musecardsPersonIdExternalReference: row.musecardsPersonId,
    name: row.name,
    counts: {
      all: modelExpected.size,
      physical: modelPhysicalExpected.length,
      digital: modelDigitalExpected.length,
      excludedOffers: excludedByModel.get(modelId) || 0,
      excludedFreePreviews: excludedFreePreviewsByModel.get(modelId) || 0,
      searchable: modelVisibleCount,
      physicalFilter: modelPhysicalVisible,
      digitalFilter: modelDigitalVisible,
      importedManifestExpected: expected.size,
      importedManifestSearchable: manifestExpectedSearchable,
      importedManifestPhysicalFilter: manifestPhysicalSearchable,
      importedManifestDigitalFilter: manifestDigitalSearchable,
      reviewedCreditAdjustments: [...reviewedCreditAdjustments.values()].filter(item => item.musecardsPersonIdExternalReference === modelId).length,
      missingImportedManifestOffers: missingImportedManifestOffers.length,
    },
    filtersPassed: liveFormatFiltersPassed && modelVisibleCount === modelExpected.size &&
      modelPhysicalVisible === modelPhysicalExpected.length && modelDigitalVisible === modelDigitalExpected.length,
    manifestCoveragePassed,
    modelMatchCount: liveFilter?.modelCount ?? null,
    searchMode: liveFilter?.searchMode || (liveMode ? "error" : "manifest_only"),
    modelFilterError: liveFilter?.error || "",
    liveModelOffers: {
      all: liveFilter?.all.length ?? null,
      physical: liveFilter?.physical.length ?? null,
      digital: liveFilter?.digital.length ?? null,
    },
    missingImportedManifestOffers,
  });
}

const result = {
  checkedAt: new Date().toISOString(),
  mode: liveMode ? "live_public_api_credits_and_frontend_marketplace_filters" : "imported_manifest_and_frontend_marketplace_filters",
  liveApi,
  databaseVerification: verification.result,
  importedModelAssociations,
  pendingAssociations,
  importedMarketplaceItems: importedItems.length,
  searchedMarketplaceItems: items.length,
  excludedListings: exclusions.length,
  excludedOfferAssociations: results.reduce((sum, row) => sum + row.counts.excludedOffers, 0),
  invalidPaidOffers,
  catalogIdentityIssues,
  marketplaceGroupingIssues,
  reviewedCrossFormatGroups,
  reviewedCreditAdjustments: [...reviewedCreditAdjustments.values()],
  missingImportedManifestAssociations: results.reduce((sum, row) => sum + row.counts.missingImportedManifestOffers, 0),
  results,
};
const output = path.join(root, "scraper/japan-models/homepage-models-verification.json");
await writeFile(output, `${JSON.stringify(result, null, 2)}\n`, "utf8");
const failures = results.filter(row => !row.filtersPassed);
const manifestCoverageFailures = results.filter(row => !row.manifestCoveragePassed);
console.log(liveMode
  ? `Verified live homepage search/format behavior for ${results.length} Japanese models against ${items.length} live marketplace offers; UI filter failures=${failures.length}; imported model-credit coverage failures=${manifestCoverageFailures.length}; missing imported associations=${result.missingImportedManifestAssociations}; paid-offer metadata issues=${invalidPaidOffers.length}`
  : `Verified homepage search and format filters for ${results.length} Japanese models; ${items.length} unique imported offers; failures=${failures.length}; paid-offer metadata issues=${invalidPaidOffers.length}`);
console.log(`Catalog work identity issues=${catalogIdentityIssues.length}`);
console.log(`Publication grouping issues=${marketplaceGroupingIssues.length}; reviewed physical/digital groups passed=${reviewedCrossFormatGroups.filter(group => group.passed).length}/${reviewedCrossFormatGroups.length}`);
if (failures.length || manifestCoverageFailures.length || invalidPaidOffers.length || catalogIdentityIssues.length || marketplaceGroupingIssues.length || reviewedCrossFormatGroups.some(group => !group.passed)) process.exitCode = 1;
