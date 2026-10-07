# Product

<!-- impeccable:product-schema 1 -->

## Platform

adaptive

## Users

Photobook collectors looking to discover and keep model, influencer, idol, and entertainer photobooks across physical and digital editions.

## Product Purpose

MuseBooks is a source-backed catalog for discovering and collecting people-centered photobooks. Success means visitors can find a relevant work, understand its editions and formats, save it, and follow source links for current market records.

## Positioning

MuseBooks organizes the subject’s photobook as a work, its physical or digital releases as editions, and retailer or marketplace records as listings. Digital delivery labels such as ebook, EPUB, or PDF do not disqualify a work when its photobook subject and content are verified.

## Operating Context

The catalog covers photobooks associated with Japan, Taiwan, China, and Malaysia. Visitors browse and save works, compare physical and digital editions, and inspect source-backed listings and prices.

## Capabilities and Constraints

- Show only source-verified works whose featured person is a model, influencer, idol, or entertainer.
- Keep physical books and verified digital photobooks in scope, even when a storefront files the digital edition under ebooks.
- Treat an uncertain subject, format, or source match as unverified; label it clearly or keep it out of the public catalog until resolved.
- Preserve the distinction between a work, its editions, and its marketplace or retailer listings.
- Do not fabricate catalog records, people, covers, prices, availability, or source verification.
- The existing project includes a web catalog and Capacitor mobile builds.

## Brand Commitments

The product name is MuseBooks.

## Evidence on Hand

- The catalog interface and API types are in `frontend/app/page.tsx` and `frontend/lib/catalog.ts`.
- The backend separates works, editions, and listings in `backend/catalog/models.go`.
- The verified catalog report records 439 published works, 528 active editions, and 334 model/artist credit labels as of 2026-10-07 (`scraper/catalog-import-report.md`).
- Six fictional scenic demo works were removed from the production database earlier in this task; their old sample data in the frontend and backend seed files is not catalog evidence.
- Four out-of-scope listings are retained as excluded history; 35 valid marketplace listings remain unlinked because their edition is not confidently identified.
- Production catalog/API data is the source for public records; a failed API connection must not fall back to fabricated samples.

## Product Principles

- Subject relevance is a publication requirement, not a search preference.
- Source evidence takes precedence over catalog breadth.
- Format describes how an edition is delivered, not whether its content is a photobook.
- Keep each work, edition, and market listing distinct and traceable.
