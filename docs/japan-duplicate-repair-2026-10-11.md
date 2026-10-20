# Japan photobook duplicate repair — 2026-10-11

Applied 206 cross-store publication groups in one database transaction, using the same edition-preserving repair approach as Fumina Suzuki. Matching is scoped to a model and exact NFKC-normalized title and publisher, ignoring whitespace and letter case. Store release dates remain edition-specific. Different volumes and title qualifiers remain distinct; ambiguous オールアザー products are excluded.

All edition IDs, source URLs, covers, offers and price observations remain intact. Redundant works are marked superseded. The importer uses the saved model-scoped identity map to prevent subsequent imports from recreating these duplicates. Per-model import manifests were regenerated after repair.

Validation: three Python importer regression tests passed; Go catalog-import checks passed; database dry run and transactional application completed. The dry-run, application and post-repair validation logs are saved beside this document. The repair command validates the original titles, model names, publishers, formats and edition ownership before changing any records.

This repair covers matching captured digital store publications. Titles with additional wording differences require separate identity evidence before grouping.
