# Fumina Suzuki homepage import and display fix

The 149 unimported offers were a local capture, not homepage database rows. The homepage also requested only marketplace sources and passed a physical format to every platform-price comparison. Its title-only search hid digital titles which omitted the model name.

The preserved capture now has all 150 offers in MuseBooks: 68 physical (67 newly imported plus one existing offer) and 82 digital (all newly imported). Original capture/report files remain historical evidence; their unimported flags describe the pre-import check. `database-import-check.json` now verifies 150 existing rows. All 15 original pilot file hashes still match.

`scraper/prepare_model_home_import.py` produces `scraper/fumina-suzuki-expanded/home-import.json` for the existing transactional catalog importer. It preserves observation timestamps, unknown availability, authorized digital access, image URLs, and publication precision. Known physical bibliography and digital product metadata provide edition dates; unmatched bundles remain unmatched. Gallery URLs remain preserved in the capture.

The homepage requests `scope=offers`, including physical marketplaces and authorized digital store offers. Omitting that scope preserves the previous marketplace-only endpoint behavior. Physical and digital groups remain separate, platform prices use the actual format, and verified model credits participate in search. The homepage displays offer totals by format and release dates at their recorded precision.

Validation: backend model/handler tests, frontend SEO/grouping/price tests, production build, read-only database comparison, and live homepage search/filter/platform-price checks. Deployment preserves previous server releases for rollback. Source prices and availability remain observations from the capture, not continuously refreshed stock guarantees.
