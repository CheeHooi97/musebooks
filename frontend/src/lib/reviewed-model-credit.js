import { normalizeSearch } from "./marketplace-groups.js";

/** Match a reviewed source correction to one exact model/title credit. */
export function reviewedCreditChangeFor(modelName, title, reviews) {
  const modelKey = normalizeSearch(modelName);
  const titleKey = normalizeSearch(title);
  if (!modelKey || !titleKey || !Array.isArray(reviews)) return null;
  return reviews.find(review => review?.action === "change" &&
    review?.evidence?.url &&
    normalizeSearch(review.model) === modelKey &&
    normalizeSearch(review.title) === titleKey) || null;
}

