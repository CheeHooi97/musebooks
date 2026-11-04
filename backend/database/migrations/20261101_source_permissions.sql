ALTER TABLE source_permissions
    ADD CONSTRAINT source_permissions_source_id_fkey
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE;

ALTER TABLE source_permissions
    ADD CONSTRAINT source_permissions_scope_check
    CHECK (scope IN ('bibliography', 'current_prices', 'used_prices', 'product_images'));

ALTER TABLE source_permissions
    ADD CONSTRAINT source_permissions_status_check
    CHECK (status IN ('pending', 'approved', 'denied', 'revoked', 'expired'));

ALTER TABLE source_permissions
    ADD CONSTRAINT source_permissions_display_mode_check
    CHECK (public_display_mode IN ('none', 'source_linked', 'attributed', 'integrated', 'separate_source_labeled'));

ALTER TABLE source_permissions
    ADD CONSTRAINT source_permissions_retention_check
    CHECK (
        retention_mode IN ('permanent', 'temporary', 'none')
        AND (retention_mode <> 'temporary' OR retention_days > 0)
        AND (retention_mode = 'temporary' OR retention_days = 0)
    );

ALTER TABLE source_permissions
    ADD CONSTRAINT source_permissions_review_evidence_check
    CHECK (
        status <> 'approved'
        OR (
            COALESCE(evidence_url LIKE 'https://%', FALSE)
            AND reviewed_at IS NOT NULL
            AND effective_at IS NOT NULL
            AND COALESCE(btrim(purpose) <> '', FALSE)
            AND COALESCE(btrim(allowed_fields) <> '', FALSE)
            AND COALESCE(btrim(allowed_uses) <> '', FALSE)
            AND retention_mode IN ('permanent', 'temporary', 'none')
            AND COALESCE(btrim(retention_policy) <> '', FALSE)
            AND COALESCE(btrim(access_method) <> '', FALSE)
            AND COALESCE(btrim(public_display_mode) <> '', FALSE)
            AND COALESCE(btrim(rightsholder) <> '', FALSE)
            AND COALESCE(btrim(territory) <> '', FALSE)
            AND (attribution_required = FALSE OR COALESCE(btrim(attribution_text) <> '', FALSE))
            AND (public_display_mode <> 'attributed' OR (attribution_required = TRUE AND COALESCE(btrim(attribution_text) <> '', FALSE)))
            AND rate_per_minute > 0
        )
    );
