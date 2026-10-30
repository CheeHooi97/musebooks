# First party digital photobook candidate

## Candidate identity and product evidence

### Takeaway

Studio BOM’s Patreon Shop gives a clear, exact digital photobook product featuring Eundam (은담), and Studio BOM’s first-party model profile describes Oh Eundam as a Korean model who works as a racing model, YouTuber, and BJ. This qualifies as a creator-led digital photo book lead, but the exact product is sold only through Patreon in the sources found.

### Cited Findings

- Studio BOM’s Patreon Shop lists **“[19 Photos] 2025 06(Jun) No.1 Eundam 은담 - Leather Office Girl”** for a one-time purchase. Its description identifies it as Eundam’s first June pictorial’s full photo book, says the images are downloadable, and lists 19 images / 20.25 MB. [Patreon Shop product](https://www.patreon.com/studiobom/shop/19-photos-2025-06-jun-no-1-eundam-eundam-1833077)
- Studio BOM’s first-party “new member” profile names model **Oh Eundam** and says she is a Korean model, racing model, YouTuber and BJ. This directly links the stage name Eundam with the Korean creator/model profile. [Studio BOM profile post](https://www.patreon.com/studiobom/posts/studio-bom-new-118010430)
- A self-authored model profile under 오은담 identifies her as a model, actor and influencer, lists the Instagram account `oh6582`, and names YouTube-channel and racing-model work. [Oh Eundam profile](https://www.filmmakers.co.kr/actorProfiles/25570801)
- Patreon’s current Terms of Use state that paid members receive only a limited license to access and view creator creations for personal, non-promotional, non-commercial use; members may not share creators’ creations in ways the creator has not authorized. [Patreon Terms of Use, §§ subscriptions and license to creations](https://www.patreon.com/policy/legal)

### Inferences

- The Shop item is a digital photobook, not a physical publication: the item is categorized as downloadable images and its description calls it a photobook.
- The creator/model identity and Korean connection are supported by Studio BOM’s own profile, rather than inferred from Korean-language text alone.
- The terms establish limits on reusing the actual paid creation; they do not expressly address the narrow act of manually recording factual bibliographic fields such as its title, creator, count and source URL.

### Gaps

- No non-Patreon creator or publisher storefront listing for this exact “Leather Office Girl” photobook was found.
- No separate permission was found for copying any photo, cover, preview image, or downloadable file to R2.

## Existing catalog check

### Takeaway

The exact title and model had no match in the reviewed local catalog files or in the live database lookup.

### Cited Findings

- Local search across `docs/`, `reports/`, and `research_notes/` found no hit for `Eundam`, `은담`, `Studio BOM`, product ID `1833077`, or `Leather Office Girl` before this note was written.
- A read-only live PostgreSQL query for work title, English title, featured name, source URL containing product ID `1833077`, and person names matching Eundam returned `workMatches: null` and `personMatches: null`.

### Inferences

- The candidate appears new to both local catalog artifacts and the live work/person catalog, based on those exact-name checks.

### Gaps

- No import manifest or read-back was created because the candidate did not pass the source policy gate described below.

## Import and media decision

### Takeaway

This pass leaves the title held: the only exact listing found is on Patreon, and no separate creator/publisher source was located that would clear the project’s Patreon-source gate. No metadata was imported and no media was uploaded to R2.

### Cited Findings

- The exact product is sold from Studio BOM’s Patreon Shop. [Patreon Shop product](https://www.patreon.com/studiobom/shop/19-photos-2025-06-jun-no-1-eundam-eundam-1833077)
- Patreon’s Terms of Use limit a member’s license for creator creations to personal, non-promotional, non-commercial access and viewing, and prohibit unauthorized sharing of those creations. [Patreon Terms of Use](https://www.patreon.com/policy/legal)

### Inferences

- The photos and any cover/preview images must not be copied from this paid Patreon product to public R2 storage without a separate license expressly covering that use.
- The live duplicate check indicates metadata import would not overwrite an existing matching title or model record; it does not override the source gate.

### Gaps

- A first-party non-Patreon product page with the same exact title, or written authorization for commercial catalog/index use and public image delivery, would be needed to revisit the hold.
